package sketch;

import java.io.PrintStream;
import java.util.HashMap;

import fileIO.ByteFile;
import fileIO.ByteStreamWriter;
import fileIO.FileFormat;
import fileIO.ReadWrite;
import shared.Parser;
import shared.PreParser;
import shared.Shared;
import shared.Timer;
import shared.Tools;
import stream.ConcurrentReadInputStream;
import stream.Read;
import structures.ByteBuilder;
import structures.ListNum;
import tax.GiToTaxid;
import tax.TaxTree;

/**
 * @author Brian Bushnell
 * @date May 9, 2016
 *
 */
public class AddSSU {
	
	/*--------------------------------------------------------------*/
	/*----------------        Initialization        ----------------*/
	/*--------------------------------------------------------------*/
	
	/**
	 * Code entrance from the command line.
	 * @param args Command line arguments
	 */
	public static void main(String[] args){
		//Start a timer immediately upon code entrance.
		Timer t=new Timer();
		
		//Create an instance of this class
		AddSSU x=new AddSSU(args);
		
		//Run the object
		x.process(t);
		
		//Close the print stream if it was redirected
		Shared.closeStream(x.outstream);
	}
	
	/**
	 * Constructor.
	 * @param args Command line arguments
	 */
	public AddSSU(String[] args){
		
		{//Preparse block for help, config files, and outstream
			PreParser pp=new PreParser(args, /*getClass()*/null, false);
			args=pp.args;
			outstream=pp.outstream;
		}
		
		//Set shared static variables prior to parsing
		ReadWrite.USE_PIGZ=ReadWrite.USE_UNPIGZ=true;
		ReadWrite.MAX_ZIP_THREADS=Shared.threads();
		
		{//Parse the arguments
			final Parser parser=parse(args);
			overwrite=parser.overwrite;
			append=parser.append;
			
			in1=parser.in1;

			out1=parser.out1;
		}
		
		fixExtensions(); //Add or remove .gz or .bz2 as needed
		checkFileExistence(); //Ensure files can be read and written
		checkStatics(); //Adjust file-related static fields as needed for this program

		ffout1=FileFormat.testOutput(out1, FileFormat.SKETCH, null, true, overwrite, append, false);
		ffssu=FileFormat.testInput(ssuFile, FileFormat.FA, null, true, false);
		ffin1=FileFormat.testInput(in1, FileFormat.SKETCH, null, true, false);
	}
	
	/*--------------------------------------------------------------*/
	/*----------------    Initialization Helpers    ----------------*/
	/*--------------------------------------------------------------*/
	
	/** Parse arguments from the command line */
	private Parser parse(String[] args){
		
		Parser parser=new Parser();
		for(int i=0; i<args.length; i++){
			String arg=args[i];
			String[] split=arg.split("=");
			String a=split[0].toLowerCase();
			String b=split.length>1 ? split[1] : null;
			if(b!=null && b.equalsIgnoreCase("null")){b=null;}

			if(a.equalsIgnoreCase("ssu") || a.equalsIgnoreCase("ssufile") || a.equalsIgnoreCase("silva")){
				ssuFile=b;
			}else if(a.equals("lines")){
				maxLines=Long.parseLong(b);
				if(maxLines<0){maxLines=Long.MAX_VALUE;}
			}else if(a.equals("verbose")){
				verbose=Tools.parseBoolean(b);
//				ByteFile1.verbose=verbose;
//				ByteFile2.verbose=verbose;
				ReadWrite.verbose=verbose;
			}else if(parser.parse(arg, a, b)){
				//do nothing
			}else{
				outstream.println("Unknown parameter "+args[i]);
				assert(false) : "Unknown parameter "+args[i];
				//				throw new RuntimeException("Unknown parameter "+args[i]);
			}
		}
		if("auto".equalsIgnoreCase(ssuFile)){ssuFile=TaxTree.defaultSsuFile();}
		
		return parser;
	}
	
	/** Add or remove .gz or .bz2 as needed */
	private void fixExtensions(){
		in1=Tools.fixExtension(in1);
		if(in1==null){throw new RuntimeException("Error - at least one input file is required.");}
	}
	
	/** Ensure files can be read and written */
	private void checkFileExistence(){
		//Ensure output files can be written
		if(!Tools.testOutputFiles(overwrite, append, false, out1)){
			outstream.println((out1==null)+", "+out1);
			throw new RuntimeException("\n\noverwrite="+overwrite+"; Can't write to output file "+out1+"\n");
		}
		
		//Ensure input files can be read
		if(!Tools.testInputFiles(false, true, in1, ssuFile)){
			throw new RuntimeException("\nCan't read some input files.\n");  
		}
		assert(in1!=null) : "Input sketch file is required";
		assert(ssuFile!=null) : "Input SSU file is required";
		
		//Ensure that no file was specified multiple times
		if(!Tools.testForDuplicateFiles(true, in1, out1, ssuFile)){
			throw new RuntimeException("\nSome file names were specified multiple times.\n");
		}
	}
	
	/** Adjust file-related static fields as needed for this program */
	private static void checkStatics(){
		//Adjust the number of threads for input file reading
		if(!ByteFile.FORCE_MODE_BF1 && !ByteFile.FORCE_MODE_BF2 && Shared.threads()>2){
			ByteFile.FORCE_MODE_BF2=true;
		}
		
//		if(!ByteFile.FORCE_MODE_BF2){
//			ByteFile.FORCE_MODE_BF2=false;
//			ByteFile.FORCE_MODE_BF1=true;
//		}
	}
	
	/*--------------------------------------------------------------*/
	/*----------------         Outer Methods        ----------------*/
	/*--------------------------------------------------------------*/
	
	void process(Timer t){
		
		ByteFile bf=ByteFile.makeByteFile(ffin1);
		ByteStreamWriter bsw=makeBSW(ffout1);
		
		processInner(bf, bsw);
		
		errorState|=bf.close();
		if(bsw!=null){errorState|=bsw.poisonAndWait();}
		
		t.stop();

		outstream.println(Tools.timeLinesBytesProcessed(t, linesProcessed, bytesProcessed, 8));
		outstream.println(Tools.linesBytesOut(linesProcessed, bytesProcessed, linesOut, bytesOut, 8, true));
		
		outstream.println();
		outstream.println(Tools.number("Sketches:", sketchCount, 8));
		outstream.println(Tools.number("SSU In:", ssuIn, 8));
		outstream.println(Tools.numberPercent("SSU Out:", ssuOut, ssuOut*100.0/sketchCount, 2, 8));
		
		if(errorState){
			throw new RuntimeException(getClass().getName()+" terminated in an error state; the output may be corrupt.");
		}
	}
	
	/*--------------------------------------------------------------*/
	/*----------------         Inner Methods        ----------------*/
	/*--------------------------------------------------------------*/
	
	private static ByteStreamWriter makeBSW(FileFormat ff){
		if(ff==null){return null;}
		ByteStreamWriter bsw=new ByteStreamWriter(ff);
		bsw.start();
		return bsw;
	}
	
	private static ConcurrentReadInputStream makeCris(FileFormat ff, PrintStream outstream){
		if(verbose){outstream.println("makeCris");}
		ConcurrentReadInputStream cris=ConcurrentReadInputStream.getReadInputStream(-1, false, ff, null);
		cris.start(); //Start the stream
		if(verbose){outstream.println("Loading "+ff.name());}
		boolean paired=cris.paired();
		assert(!paired);
//		if(!ffin1.samOrBam()){outstream.println("Input is being processed as "+(paired ? "paired" : "unpaired"));}
		return cris;
	}
	
	public static HashMap<Integer, byte[]> loadSSU(FileFormat ff, PrintStream outstream){
		ConcurrentReadInputStream cris=makeCris(ff, outstream);
		HashMap<Integer, byte[]> map=new HashMap<Integer, byte[]>(1000000);
		
		//Grab the first ListNum of reads
		ListNum<Read> ln=cris.nextList();

		//Check to ensure pairing is as expected
		if(ln!=null && !ln.isEmpty()){
//			if(verbose){outstream.println("Fetched "+ln.size()+" reads.");}
			Read r=ln.get(0);
			assert(ff.samOrBam() || (r.mate!=null)==cris.paired());
		}

		//As long as there is a nonempty read list...
		while(ln!=null && ln.size()>0){
			if(verbose){outstream.println("Fetched "+ln.size()+" reads.");}
			for(Read r : ln){
				final int tid=GiToTaxid.getID(r.id);
				if(tid>=0 && r.length()>1000){
					byte[] old=map.get(tid);
					if(old==null || old.length<r.length()){map.put(tid, r.bases);}
				}
			}
			cris.returnList(ln.id, ln.list==null || ln.list.isEmpty());

			//Fetch a new list
			ln=cris.nextList();
		}

		//Notify the input stream that the final list was used
		if(ln!=null){
			cris.returnList(ln.id, ln.list==null || ln.list.isEmpty());
		}
//		errorState|=ReadWrite.closeStream(cris);
		ReadWrite.closeStream(cris);
		
		return map;
	}
	
	private void processInner(ByteFile bf, ByteStreamWriter bsw){
		
		HashMap<Integer, byte[]> map=loadSSU(ffssu, outstream);
		
		byte[] line=bf.nextLine();
//		ByteBuilder bb=new ByteBuilder();
		
		final byte[] ssuBytes="SSU:".getBytes();
		
		while(line!=null){
			if(line.length>0){
				if(maxLines>0 && linesProcessed>=maxLines){break;}
				linesProcessed++;
				bytesProcessed+=(line.length+1);
				
				final boolean header=(line[0]=='#');

				linesOut++;
				bytesOut+=(line.length+1);
				ByteBuilder bb=new ByteBuilder(2000);
				
				if(header){
					if(Tools.startsWith(line, "#SZ:")){
						sketchCount++;
//						private long sketchCount=0;
//						private long ssuIn=0;
//						private long ssuOut=0;
						
						if(Tools.contains(line, ssuBytes, 0)){//nothing to do
							bsw.println(line);
						}else{
							byte[] ssu=null;
							final int tid=parseTaxID(line);
							if(tid>=0){ssu=map.get(tid);}
							if(ssu==null){
								bsw.println(line);
							}else{
								bsw.print(line);
								bb.append("\tSSU:").append(ssu.length).nl();
								bb.append("#SSU:").append(ssu).nl();
								bsw.print(bb);
								
								linesOut++;
								bytesOut+=(bb.length-1);
								ssuOut++;
								bb.clear();
							}
						}
					}else{
						assert(Tools.startsWith(line, "#SSU:") || Tools.startsWith(line, "##")) : new String(line);
						bsw.println(line);
						ssuIn++;
						ssuOut++;
					}
				}else{
					bsw.println(line);
				}
			}
			line=bf.nextLine();
		}
	}
	
	int parseTaxID(byte[] line){
		String[] split=Tools.tabPattern.split(new String(line));
		for(String s : split){
			if(s.startsWith("ID:") || s.startsWith("TAXID:")){
				final int colon=s.indexOf(':');
				final String sub=s.substring(colon+1);
				return Integer.parseInt(sub);
			}
		}
		return -1;
	}
	
	/*--------------------------------------------------------------*/
	/*----------------            Fields            ----------------*/
	/*--------------------------------------------------------------*/
	
	private String in1=null;
	private String out1=null;
	private String ssuFile="auto";
	
	/*--------------------------------------------------------------*/
	
	private long linesProcessed=0;
	private long linesOut=0;
	private long bytesProcessed=0;
	private long bytesOut=0;
	
	private long sketchCount=0;
	private long ssuIn=0;
	private long ssuOut=0;
	
	private long maxLines=Long.MAX_VALUE;
	
	/*--------------------------------------------------------------*/
	/*----------------         Final Fields         ----------------*/
	/*--------------------------------------------------------------*/
	
	private final FileFormat ffin1;
	private final FileFormat ffout1;
	private final FileFormat ffssu;
	
	/*--------------------------------------------------------------*/
	/*----------------        Common Fields         ----------------*/
	/*--------------------------------------------------------------*/
	
	private PrintStream outstream=System.err;
	public static boolean verbose=false;
	public boolean errorState=false;
	private boolean overwrite=false;
	private boolean append=false;
	
}
