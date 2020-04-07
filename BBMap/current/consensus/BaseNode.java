package consensus;

import dna.AminoAcid;
import shared.Tools;
import stream.FASTQ;
import structures.ByteBuilder;

/**
 * A placeholder for a base.
 * Tracks counts of bases seen at that position.
 * Maintains edges to observed next bases.
 * 
 * @author Brian Bushnell
 * @date September 6, 2019
 *
 */
public class BaseNode extends BaseGraphPart implements Comparable<BaseNode> {
	
	/*--------------------------------------------------------------*/
	/*----------------        Initialization        ----------------*/
	/*--------------------------------------------------------------*/
	
	public BaseNode(char refBase_, int type_, int rpos_){
		this((byte)refBase_, type_, rpos_);
	}
	
	public BaseNode(byte refBase_, int type_, int rpos_){
		super(type_);
		refBase=refBase_;
		rpos=rpos_;
		acgtWeight=(type==DEL ? null : new int[4]);
		acgtCount=(type==DEL ? null : new int[4]);
	}
	
	/*--------------------------------------------------------------*/
	/*----------------           Methods            ----------------*/
	/*--------------------------------------------------------------*/
	
	/** Add a traversal of the designated base and quality */
	public void add(byte base, int quality){
		int num=AminoAcid.baseToNumber[base];
		if(num>=0 && type!=DEL){
			acgtWeight[num]+=quality;
			acgtCount[num]++;
		}
		countSum++;
		weightSum+=quality;
	}
	
//	public byte consensus() {
//		assert(type!=DEL);
//		int maxPos=AminoAcid.baseToNumber0[refBase];
//		int max=acgtWeight[maxPos];
//		if(max*2>=weight && AminoAcid.isFullyDefined(refBase)){return refBase;}//Common case
//		if(maxPos<0){maxPos=0;}
//		
//		for(int i=0; i<acgtWeight.length; i++){
//			int weight=acgtWeight[i];
//			int depth=acgtCount[i];
//			if(weight>max && depth>=minDepth){
//				max=weight;
//				maxPos=i;
//			}
//		}
//		return AminoAcid.numberToBase[maxPos];
//	}
	
	public byte consensus(byte[] r) {
		assert(type!=DEL);
		if(onlyConvertNs && type==REF && refBase!='N'){
			r[0]=refBase;
			r[1]=20;
			return refBase;
		}
		int maxPos=AminoAcid.baseToNumber0[refBase];
		int maxWeight=acgtWeight[maxPos];
		int maxDepth=acgtCount[maxPos];
//		long sum=Tools.sum(acgtWeight);
		
		if(maxWeight*2<weightSum){//Uncommon case
			for(int i=0; i<acgtWeight.length; i++){
				int x=acgtWeight[i];
				if(x>maxWeight){
					maxWeight=x;
					maxPos=i;
				}
			}
		}
		
		if(type==REF){
			byte b=AminoAcid.numberToBase[maxPos];
			float af=maxDepth/(float)countSum;
			float maf=(refBase=='N' ? MAF_noref : MAF_sub);
			if(af<maf || maxDepth<minDepth){
				r[0]=refBase;
				r[1]=(refBase=='N' ? (byte)0 : (byte)2);
			}else{
				r[0]=AminoAcid.numberToBase[maxPos];
				double quality=Tools.mid(2, 41, 10*Math.log10(maxWeight/Tools.max(0.01f, weightSum)));
				r[1]=(byte)(quality+FASTQ.ASCII_OFFSET);
			}
		}else{
			assert(type==INS);
			r[0]=AminoAcid.numberToBase[maxPos];
			double quality=Tools.mid(2, 41, 10*Math.log10(maxWeight/Tools.max(0.01f, weightSum)));
			r[1]=(byte)(quality+FASTQ.ASCII_OFFSET);
		}
		return r[0];
	}
	
	
	
	/** Add a traversal of the designated quality */
	void increment(byte base, int quality){add(base, quality);}
	
	@Override
	public final String partString(){return "Node";}
	
	@Override
	public ByteBuilder toText(){
		ByteBuilder bb=new ByteBuilder();
		bb.append('(');
		bb.append(partString()).comma().append(rpos).comma().append(typeString());
		for(int i=0; i<4; i++){bb.comma().append(acgtWeight[i]);}
		bb.space();
		if(refEdge!=null){bb.comma().append("REF:").append(refEdge.weightSum);}
		if(insEdge!=null){bb.comma().append("INS:").append(insEdge.weightSum);}
		if(delEdge!=null){bb.comma().append("DEL:").append(delEdge.weightSum);}
//		if(delEdges!=null){
//			for(BaseNode be : delEdges){
//				bb.comma().append(be.toText());
//			}
//		}
		bb.append(')');
		return bb;
	}
	
	@Override
	public int compareTo(BaseNode b) {
		int dif=weightSum-b.weightSum;
		if(dif!=0){return dif;}
		dif=countSum-b.countSum;
		if(dif!=0){return dif;}
		return type-b.type;
	}
	
	/*--------------------------------------------------------------*/
	/*----------------            Fields            ----------------*/
	/*--------------------------------------------------------------*/
	
	/** Number of times this node has been traversed */
	public int countSum;
	/** Sum of scores of traversals.  Generally, sum of quality scores of this or adjacent bases.
	 * Probably equal to sum of acgt. */
	public int weightSum;
	
	public final int rpos;
	
	public final byte refBase;
	public final int[] acgtWeight;
	public final int[] acgtCount;
	
	//These fields are not really necessary
	public BaseNode refEdge;
	public BaseNode insEdge;
	public BaseNode delEdge;
	
}
