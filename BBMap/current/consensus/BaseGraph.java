package consensus;

import shared.Tools;
import stream.FASTQ;
import stream.Read;
import structures.ByteBuilder;

/**
 * A graph of the possible alignments of a reference sequence.
 * 
 * @author Brian Bushnell
 * @date September 6, 2019
 *
 */
public class BaseGraph extends ConsensusObject {
	
	/*--------------------------------------------------------------*/
	/*----------------        Initialization        ----------------*/
	/*--------------------------------------------------------------*/
	
	public BaseGraph(String name_, byte[] bases_, long numericID_){
		name=name_;
		original=bases_;
		numericID=numericID_;

		ref=new BaseNode[original.length];
		del=new BaseNode[original.length];
		for(int i=0; i<original.length; i++){
			byte b=original[i];
			ref[i]=new BaseNode(b, REF, i);
			del[i]=new BaseNode(b, DEL, i);
		}
		for(int i=0; i<ref.length-1; i++){
			ref[i].refEdge=ref[i+1];
		}
		for(int i=0; i<ref.length; i++){
			ref[i].add(original[i], 1);
		}
	}
	
	/*--------------------------------------------------------------*/
	/*----------------           Methods            ----------------*/
	/*--------------------------------------------------------------*/
	
	/** This method should be threadsafe */
	public void add(Read r){
		r.toLongMatchString(false);
		final byte[] match=r.match;
		final byte[] bases=r.bases;
		final byte[] quals=r.quality;
		assert(match!=null && bases!=null);
		final int start=r.start;
		int qpos=0, rpos=start;
		byte prevState='?';
		BaseNode prevNode=(rpos<=0 ? null : ref[rpos-1]);
		
		final int mapq=(r.samline==null ? 20 : r.samline.mapq+1);
		int msSum=0;
		int delSum=0;
		int insSum=0;
		long qualSum=0;
		for(int mpos=0; mpos<match.length && rpos<ref.length; mpos++){
			final byte m=match[mpos];
			final BaseNode next;
			final int q;
			assert(qpos<bases.length) : "\n"+r+"\n"+r.samline+"\n"+r.length()+", "+r.start+", "+r.stop+", "+
				r.samline.calcCigarLength(true, false)+", "+r.samline.calcCigarReadLength(true, false);
			final byte b=bases[qpos];
			
//			System.err.println("mpos="+mpos+", qpos="+qpos+", rpos="+rpos+", b="+Character.toString((char)b)+", m="+Character.toString((char)m)+", prev="+prevNode);
			
			if(m=='m' || m=='S' || m=='N'){
				next=(rpos<0 ? null : ref[rpos]);
				q=(quals==null ? 20 : quals[qpos]);

				qpos++;
				rpos++;
				msSum++;
				qualSum+=q;
			}else if(m=='D'){
				next=(rpos<0 ? null : del[rpos]);
				q=(quals==null ? 20 : (quals[qpos]+quals[qpos+1])/2);

				rpos++;
				delSum++;
			}else if(m=='I'){
				assert(prevNode!=null) : new String(r.match+"\n"+r.samline); //Alignments must not start with I.
				synchronized(prevNode) {
					if(prevNode.insEdge==null){
						prevNode.insEdge=new BaseNode('.', INS, rpos);
					}
					next=prevNode.insEdge;
				}
				q=(quals==null ? 20 : quals[qpos]);

				qpos++;
				insSum++;
				qualSum+=q;
			}else if(m=='C'){
				next=null;
				
				q=(quals==null ? 20 : quals[qpos]);
				qpos++;
				rpos++;
			}else{
				next=null;
				
				q=1;
				assert(false) : Character.toString((char)m)+"\n"+new String(match)+"\n"+r.id;
			}
			
			if(next!=null){
//				System.err.println("Adding "+Character.toString(b)+" to "+next);
				int weight=q+1;
				if(useMapq){
					weight=(int)(Math.ceil(Math.sqrt(q*mapq)));
				}
				synchronized(next){
					next.add(b, weight);
				}
			}
			prevNode=next;
			prevState=m;
		}
		
		synchronized(this){
			readTotal++;
			baseTotal+=bases.length;
			symbolTotal+=match.length;
			msTotal+=msSum;
			insTotal+=insSum;
			delTotal+=delSum;
			qualTotal+=qualSum;
		}
	}
	
	@Override
	public ByteBuilder toText() {
		System.err.println("...");
		ByteBuilder bb=new ByteBuilder();
		bb.append(name).append(':');
		bb.append('{');
		if(ref.length>0){bb.append(ref[0].toText());}
		for(int i=0; i<ref.length; i++){
			if(i>0){bb.comma();}
			bb.append(ref[i].toText());
		}
		bb.append('}');
		return bb;
	}
	
	public Read traverse() {
		final ByteBuilder bb=new ByteBuilder();
		final ByteBuilder bq=new ByteBuilder();

//		System.err.println("rpos\tdw\trw\tiw");
		final byte[] temp=new byte[2];
		for(int i=0; i<ref.length; i++) {
			
			final BaseNode dnode=del[i];
			final BaseNode rnode=ref[i];
			BaseNode inode=(rnode.insEdge==null ? dummy : rnode.insEdge);
			
			final int dw=dnode.weightSum;
			final int rw=rnode.weightSum;

			final int dc=dnode.countSum;
			final int rc=rnode.countSum;
			
			final float afMult=1f/(dc+rc);
			final float daf=dc*afMult;
			
			long weightSum=dw+rw;
			
//			System.err.println(i+"\t"+dw+"\t"+rw+"\t"+iw);
			
			if(rw>=dw || daf<MAF_del || noIndels){//Common case
				{
					rnode.consensus(temp);
					byte b=temp[0];
					byte q=temp[1];
					bb.append(b);
//					System.err.println(i+": "+Character.toString(b));
					assert(b!='.') : rnode+", "+rnode.weightSum+", "+weightSum;
					double quality=Tools.mid(2, 41, 10*Math.log10(rw/Tools.max(0.01f, weightSum-rw)));
					bq.append((byte)(Tools.min(q, quality)+FASTQ.ASCII_OFFSET));
					if(b==rnode.refBase){
						refCount++;
					}else{
						subCount++;
					}
				}
				
				//Then add inodes
				while(inode!=null && !noIndels && inode.weightSum>=(weightSum-inode.weightSum) && inode.countSum*afMult>=MAF_ins){
					inode.consensus(temp);
					byte b=temp[0];
					byte q=temp[1];
					assert(b!='.') : inode+", "+inode.weightSum+", "+weightSum;
					bb.append(b);
//					System.err.println(i+": "+Character.toString(b));
					double quality=Tools.mid(2, 41, 10*Math.log10(inode.weightSum/(rw+dw)));
					bq.append((byte)(Tools.min(q, quality)+FASTQ.ASCII_OFFSET));
					insCount++;
					inode=inode.insEdge;
				}
			}else{
				//Deletion, do nothing
				delCount++;
			}
		}
		
		return new Read(bb.toBytes(), bq.toBytes(), name, numericID);
	}
	
	/*--------------------------------------------------------------*/
	/*----------------            Fields            ----------------*/
	/*--------------------------------------------------------------*/

	public long readTotal;
	public long baseTotal;
	public long symbolTotal;
	public long msTotal;
	public long insTotal;
	public long delTotal;
	public long qualTotal;
	
	
	public int subCount=0;
	public int refCount=0;
	public int delCount=0;
	public int insCount=0;
	
	/*--------------------------------------------------------------*/
	/*----------------         Final Fields         ----------------*/
	/*--------------------------------------------------------------*/
	
	public final String name;
	public final byte[] original;
	public final long numericID;
	//For ref nodes, calculate total outgoing weight.
	//Choose ins only if it is plurality allele. (or alternatively, majority allele).
	//But return to ref once it is no longer the majority/plurality of the outgoing weight.
	
	public final BaseNode[] ref;
	public final BaseNode[] del;
	
	/*--------------------------------------------------------------*/
	/*----------------        Static Fields         ----------------*/
	/*--------------------------------------------------------------*/
	
	public static final BaseNode dummy=new BaseNode('.', INS, 0);
	
	public static boolean useMapq=false;

}
