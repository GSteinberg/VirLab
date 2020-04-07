package var2;

import java.io.PrintStream;
import java.util.ArrayList;
import java.util.HashMap;

import fileIO.ByteFile;
import fileIO.FileFormat;
import fileIO.ReadWrite;
import shared.Parser;
import shared.PreParser;
import shared.ReadStats;
import shared.Shared;
import shared.Timer;
import shared.Tools;
import stream.ConcurrentReadInputStream;
import stream.ConcurrentReadOutputStream;
import stream.FASTQ;
import stream.FastaReadInputStream;
import stream.Read;
import structures.ByteBuilder;
import structures.ListNum;

/**
 * Applies variants
 * 
 * @author Brian Bushnell
 * @date August 27, 2019
 *
 */
public class ApplyVariants {
	
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
		ApplyVariants x=new ApplyVariants(args);
		
		//Run the object
		x.process(t);
		
		//Close the print stream if it was redirected
		Shared.closeStream(x.outstream);
	}
	
	/**
	 * Constructor.
	 * @param args Command line arguments
	 */
	public ApplyVariants(String[] args){
		
		{//Preparse block for help, config files, and outstream
			PreParser pp=new PreParser(args, getClass(), false);
			args=pp.args;
			outstream=pp.outstream;
		}
		
		//Set shared static variables prior to parsing
		ReadWrite.USE_PIGZ=ReadWrite.USE_UNPIGZ=true;
		ReadWrite.MAX_ZIP_THREADS=Shared.threads();
		Shared.capBuffers(4); //Only for singlethreaded programs
		
		{//Parse the arguments
			final Parser parser=parse(args);
			Parser.processQuality();
			
			maxReads=parser.maxReads;
			overwrite=ReadStats.overwrite=parser.overwrite;
			append=ReadStats.append=parser.append;
			
			in1=parser.in1;
			extin=parser.extin;

			out1=parser.out1;
			extout=parser.extout;
		}

		doPoundReplacement(); //Replace # with 1 and 2
		adjustInterleaving(); //Make sure interleaving agrees with number of input and output files
		fixExtensions(); //Add or remove .gz or .bz2 as needed
		checkFileExistence(); //Ensure files can be read and written
		checkStatics(); //Adjust file-related static fields as needed for this program 
		
		//Create output FileFormat objects
		ffout1=FileFormat.testOutput(out1, FileFormat.FASTA, extout, true, overwrite, append, ordered);

		//Create input FileFormat objects
		ffin1=FileFormat.testInput(in1, FileFormat.FASTA, extin, true, true);
		ffvcf=FileFormat.testInput(inVcf, FileFormat.VCF, null, true, true);
	}
	
	/*--------------------------------------------------------------*/
	/*----------------    Initialization Helpers    ----------------*/
	/*--------------------------------------------------------------*/
	
	/** Parse arguments from the command line */
	private Parser parse(String[] args){
		
		//Create a parser object
		Parser parser=new Parser();
		
		//Set any necessary Parser defaults here
		//parser.foo=bar;
		
		//Parse each argument
		for(int i=0; i<args.length; i++){
			String arg=args[i];
			
			//Break arguments into their constituent parts, in the form of "a=b"
			String[] split=arg.split("=");
			String a=split[0].toLowerCase();
			String b=split.length>1 ? split[1] : null;
			if(b!=null && b.equalsIgnoreCase("null")){b=null;}
			
			if(a.equals("verbose")){
				verbose=Tools.parseBoolean(b);
			}else if(a.equals("vcf") || a.equals("vars")){
				inVcf=b;
			}else if(a.equals("parse_flag_goes_here")){
				long fake_variable=Tools.parseKMG(b);
				//Set a variable here
			}else if(parser.parse(arg, a, b)){//Parse standard flags in the parser
				//do nothing
			}else{
				outstream.println("Unknown parameter "+args[i]);
				assert(false) : "Unknown parameter "+args[i];
			}
		}
		
		return parser;
	}
	
	/** Replace # with 1 and 2 in headers */
	private void doPoundReplacement(){
		
		//Ensure there is an input file
		if(in1==null || inVcf==null){throw new RuntimeException("Error - one sequence and one vcf file are required.");}
	}
	
	/** Add or remove .gz or .bz2 as needed */
	private void fixExtensions(){
		in1=Tools.fixExtension(in1);
		inVcf=Tools.fixExtension(inVcf);
	}
	
	/** Ensure files can be read and written */
	private void checkFileExistence(){
		//Ensure output files can be written
		if(!Tools.testOutputFiles(overwrite, append, false, out1)){
			outstream.println((out1==null)+", "+out1);
			throw new RuntimeException("\n\noverwrite="+overwrite+"; Can't write to output files "+out1+"\n");
		}
		
		//Ensure input files can be read
		if(!Tools.testInputFiles(false, true, in1, inVcf)){
			throw new RuntimeException("\nCan't read some input files.\n");  
		}
		
		//Ensure that no file was specified multiple times
		if(!Tools.testForDuplicateFiles(true, in1, inVcf, out1)){
			throw new RuntimeException("\nSome file names were specified multiple times.\n");
		}
	}
	
	/** Make sure interleaving agrees with number of input and output files */
	private void adjustInterleaving(){
		FASTQ.FORCE_INTERLEAVED=false;
		FASTQ.TEST_INTERLEAVED=false;
	}
	
	/** Adjust file-related static fields as needed for this program */
	private static void checkStatics(){
		//Adjust the number of threads for input file reading
		if(!ByteFile.FORCE_MODE_BF1 && !ByteFile.FORCE_MODE_BF2 && Shared.threads()>2){
			ByteFile.FORCE_MODE_BF2=true;
		}
		
		assert(FastaReadInputStream.settingsOK());
	}
	
	/*--------------------------------------------------------------*/
	/*----------------         Outer Methods        ----------------*/
	/*--------------------------------------------------------------*/

	/** Create read streams and process all data */
	void process(Timer t){
		
		VCFFile vfile=new VCFFile(ffvcf);
		
		//Load vcf
		if(ScafMap.defaultScafMap()==null){
			ScafMap.setDefaultScafMap(vfile.toScafMap(null), ffvcf.name());
		}
		
		ArrayList<VCFLine> lines=vfile.lines(true);
		varMap=new HashMap<String, ArrayList<Var>>(ScafMap.defaultScafMap().size());
		
		for(VCFLine line : lines){
			ArrayList<Var> value=varMap.get(line.scaf);
			if(value==null){
				value=new ArrayList<Var>();
				varMap.put(line.scaf, value);
			}
			value.add(line.toVar());
		}
		
		//Create a read input stream
		final ConcurrentReadInputStream cris=makeCris();
		
		//Optionally create a read output stream
		final ConcurrentReadOutputStream ros=makeCros();
		
		//Reset counters
		readsProcessed=readsOut=0;
		basesProcessed=basesOut=0;
		
		//Process the read stream
		processInner(cris, ros);
		
		if(verbose){outstream.println("Finished; closing streams.");}
		
		//Write anything that was accumulated by ReadStats
		errorState|=ReadStats.writeAll();
		//Close the read streams
		errorState|=ReadWrite.closeStreams(cris, ros);
		
		//Report timing and results
		t.stop();
		outstream.println(Tools.timeReadsBasesProcessed(t, readsProcessed, basesProcessed, 8));
		outstream.println(Tools.readsBasesOut(readsProcessed, basesProcessed, readsOut, basesOut, 8, false));
		
		//Throw an exception of there was an error in a thread
		if(errorState){
			throw new RuntimeException(getClass().getName()+" terminated in an error state; the output may be corrupt.");
		}
	}
	
	/*--------------------------------------------------------------*/
	/*----------------         Inner Methods        ----------------*/
	/*--------------------------------------------------------------*/
	
	private ConcurrentReadInputStream makeCris(){
		ConcurrentReadInputStream cris=ConcurrentReadInputStream.getReadInputStream(maxReads, true, ffin1, null);
		cris.start(); //Start the stream
		if(verbose){outstream.println("Started cris");}
		boolean paired=cris.paired();
		if(!ffin1.samOrBam()){outstream.println("Input is being processed as "+(paired ? "paired" : "unpaired"));}
		return cris;
	}
	
	private ConcurrentReadOutputStream makeCros(){
		if(ffout1==null){return null;}

		//Select output buffer size based on whether it needs to be ordered
		final int buff=4;
		
		final ConcurrentReadOutputStream ros=ConcurrentReadOutputStream.getStream(ffout1, null, buff, null, false);
		ros.start(); //Start the stream
		return ros;
	}
	
	/** Iterate through the reads */
	void processInner(final ConcurrentReadInputStream cris, final ConcurrentReadOutputStream ros){
		
		//Do anything necessary prior to processing
		
		{
			//Grab the first ListNum of reads
			ListNum<Read> ln=cris.nextList();

			//Check to ensure pairing is as expected
			if(ln!=null && !ln.isEmpty()){
				Read r=ln.get(0);
				assert(ffin1.samOrBam() || (r.mate!=null)==cris.paired());
			}

			//As long as there is a nonempty read list...
			while(ln!=null && ln.size()>0){
//				if(verbose){outstream.println("Fetched "+reads.size()+" reads.");} //Disabled due to non-static access
				
				processList(ln, cris, ros);

				//Fetch a new list
				ln=cris.nextList();
			}
			
			//Notify the input stream that the final list was used
			if(ln!=null){
				cris.returnList(ln.id, ln.list==null || ln.list.isEmpty());
			}
		}
		
		//Do anything necessary after processing
		
	}
	
	/**
	 * Process a list of Reads.
	 * @param ln The list.
	 * @param cris Read Input Stream
	 * @param ros Read Output Stream for reads that will be retained
	 */
	void processList(ListNum<Read> ln, final ConcurrentReadInputStream cris, final ConcurrentReadOutputStream ros){

		//Grab the actual read list from the ListNum
		final ArrayList<Read> reads=ln.list;
		
		//Loop through each read in the list
		for(int idx=0; idx<reads.size(); idx++){
			final Read r=reads.get(idx);
			
			//Validate reads in worker threads
			if(!r.validated()){r.validate(true);}

			//Track the initial length for statistics
			final int initialLength1=r.length();

			//Increment counters
			readsProcessed+=r.pairCount();
			basesProcessed+=initialLength1;

			Read mutant=processRead(r);
			reads.set(idx, mutant);
			readsOut+=mutant.pairCount();
			basesOut+=mutant.pairLength();
		}

		//Output reads to the output stream
		if(ros!=null){ros.add(reads, ln.id);}

		//Notify the input stream that the list was used
		cris.returnList(ln);
//		if(verbose){outstream.println("Returned a list.");} //Disabled due to non-static access
	}
	
	
	/**
	 * Process a single read.
	 * @param r Read 1
	 */
	Read processRead(final Read r){
		String name=r.id;
		final byte[] bases=r.bases;
		ArrayList<Var> vars=varMap.get(name);
		if(vars==null){return r;}
		HashMap<Integer, Var> map=new HashMap<Integer, Var>();
		for(Var v : vars){
			Integer key=v.start;
			Var old=map.get(key);
			if(old==null || old.alleleCount()<v.alleleCount()){
				map.put(key, v);
			}
		}
		
		ByteBuilder bb=new ByteBuilder();
		for(int i=0; i<bases.length; ){
			Var v=map.get(i);
			if(v==null){
				bb.append(bases[i]);
				i++;
			}else{
				int reflen=v.reflen();
				int readlen=v.readlen();
				if(readlen>0){
					bb.append(v.allele);
				}
				if(reflen==0){
					bb.append(bases[i]);
					i++;
				}else{
					i+=reflen;
				}
			}
		}
		
		Read mutant=new Read(bb.toBytes(), null, r.id, r.numericID);
		return mutant;
	}
	
	/*--------------------------------------------------------------*/
	/*----------------            Fields            ----------------*/
	/*--------------------------------------------------------------*/

	/** Primary input file path */
	private String in1=null;
	/** Variant input file */
	private String inVcf;

	/** Primary output file path */
	private String out1=null;
	
	/** Override input file extension */
	private String extin=null;
	/** Override output file extension */
	private String extout=null;
	
	HashMap<String, ArrayList<Var>> varMap;
	
	/*--------------------------------------------------------------*/

	/** Number of reads processed */
	protected long readsProcessed=0;
	/** Number of bases processed */
	protected long basesProcessed=0;

	/** Number of reads retained */
	protected long readsOut=0;
	/** Number of bases retained */
	protected long basesOut=0;

	/** Quit after processing this many input reads; -1 means no limit */
	private long maxReads=-1;
	
	/*--------------------------------------------------------------*/
	/*----------------         Final Fields         ----------------*/
	/*--------------------------------------------------------------*/

	/** Primary input file */
	private final FileFormat ffin1;
	/** Variant input file */
	private final FileFormat ffvcf;
	
	/** Primary output file */
	private final FileFormat ffout1;
	
	/*--------------------------------------------------------------*/
	/*----------------        Common Fields         ----------------*/
	/*--------------------------------------------------------------*/
	
	/** Print status messages to this output stream */
	private PrintStream outstream=System.err;
	/** Print verbose messages */
	public static boolean verbose=false;
	/** True if an error was encountered */
	public boolean errorState=false;
	/** Overwrite existing output files */
	private boolean overwrite=false;
	/** Append to existing output files */
	private boolean append=false;
	/** This flag has no effect on singlethreaded programs */
	private final boolean ordered=false;
	
}
