package prok;

import java.util.ArrayList;
import java.util.HashMap;
import fileIO.FileFormat;
import fileIO.TextStreamWriter;
import server.ServerTools;
import shared.Tools;
import template.ThreadWaiter;

/** Crawls ncbi's ftp site to download genomes and annotations */
public class FetchProks {
	
	public static void main(String[] args){
		//ftp://ftp.ncbi.nih.gov:21/genomes/refseq/bacteria/
		
		String baseAddress=args[0];
		String out=args.length>1 ? args[1] : "stdout";
		if(args.length>2){
			allowSameGenus=Tools.parseBoolean(args[2]);
			System.err.println("Set allowSameGenus="+allowSameGenus);
		}
		TextStreamWriter tsw=new TextStreamWriter(out, true, false, false, FileFormat.TEXT);
		tsw.start();

//		iterateOuter(baseAddress, tsw);
		ArrayList<String> contents=ServerTools.listDirectory(baseAddress, retries);
		
		int threads=9;
		ArrayList<ProcessThread> alpt=new ArrayList<ProcessThread>(threads);
		for(int i=0; i<threads; i++){
			alpt.add(new ProcessThread(contents, tsw, i, threads));
		}
		for(ProcessThread pt : alpt){pt.start();}
		boolean success=ThreadWaiter.waitForThreads(alpt);
		
		for(ProcessThread pt : alpt){
			totalSpecies+=pt.totalSpeciesT;
			totalGenus+=pt.totalGenusT;
			totalGenomes+=pt.totalGenomesT;
		}
		System.err.println("Total Genomes: "+totalGenomes);
		System.err.println("Total Species: "+totalSpecies);
		System.err.println("Total Genuses: "+totalGenus);
		
		tsw.poisonAndWait();
		assert(success);
	}
	
	static class ProcessThread extends Thread {
		
		ProcessThread(ArrayList<String> speciesList_, TextStreamWriter tsw_, int tid_, int threads_){
			speciesList=speciesList_;
			tsw=tsw_;
			tid=tid_;
			threads=threads_;
		}
		
		@Override
		public void run(){
			for(String s : speciesList){
//				char c=s.charAt(0);
//				if(c%threads==tid) {
//					processSpecies(s);
//				}
				if((s.hashCode()&Integer.MAX_VALUE)%threads==tid) {
					processSpecies(s);
				}
			}
		}
		
		void processSpecies(String species){
			String genus=getGenus(species);
			if(genus!=null){
				boolean present=seen.containsKey(genus);
				if(!present || allowSameGenus){
					int found=examineSpecies(species, tsw);
					if(found>=1){
						totalSpeciesT++;
						totalGenomesT+=found;
						if(present){
							seen.put(genus, seen.get(genus)+found);
						}else{
							seen.put(genus, found==1 ? one : found);
							totalGenusT++;
						}
					}
				}else{
					if(verbose){System.err.println("same genus: "+species+"\n"+genus);}
				}
			}else{
				if(verbose){System.err.println("bad species: "+species+"\n"+genus);}
			}
		}
		
		final ArrayList<String> speciesList;
		final int tid;
		final int threads;
		HashMap<String, Integer> seen=new HashMap<String, Integer>();
		final TextStreamWriter tsw;
		
		int totalSpeciesT=0;
		int totalGenusT=0;
		int totalGenomesT=0;
	}
	
	static int iterateOuter(String baseAddress, TextStreamWriter tsw){
		ArrayList<String> contents=ServerTools.listDirectory(baseAddress, retries);
		
		HashMap<String, Integer> seen=new HashMap<String, Integer>();
		final Integer one=1;
		for(String species : contents){
//			System.err.println(species);
			String genus=getGenus(species);
			if(genus!=null){
				boolean present=seen.containsKey(genus);
				if(!present || allowSameGenus){
					int found=examineSpecies(species, tsw);
					if(found>=1){
						totalSpecies++;
						totalGenomes+=found;
						if(present){
							seen.put(genus, seen.get(genus)+found);
						}else{
							seen.put(genus, found==1 ? one : found);
							totalGenus++;
						}
					}
				}else{
					if(verbose){System.err.println("same genus: "+species+"\n"+genus);}
				}
			}else{
				if(verbose){System.err.println("bad species: "+species+"\n"+genus);}
			}
		}
		return totalGenus;
	}
	
	static String getGenus(String path){
		//Candidatus_Hamiltonella
		String name=path.substring(path.lastIndexOf('/')+1);
		if(name.startsWith("Candidatus_")){name=name.substring("Candidatus_".length());}
		int under=name.indexOf('_');
		if(under>0){
			return name.substring(0, under);
		}else{
			return null;
		}
	}
	
	static String getSpecies(String path){
		//Candidatus_Hamiltonella
		String name=path.substring(path.lastIndexOf('/')+1);
		if(name.startsWith("Candidatus_")){name=name.substring("Candidatus_".length());}
		return name;
	}
	
	static int examineSpecies(String baseAddress, TextStreamWriter tsw){
		if(verbose){System.err.println("examineSpecies: "+baseAddress);}
		String speciesName=getSpecies(baseAddress);
		ArrayList<String> contents=ServerTools.listDirectory(baseAddress, retries);
//		System.err.println("B: "+contents);
		int found=0;
		for(String s : contents){
//			System.err.println(s);
			if(s.contains("reference")){
//				System.err.println("Looking at '"+s+"'");
				found+=examineAssemblies(s, tsw, speciesName);
			}
		}
		if(found>0){return found;}
		for(String s : contents){
//			System.err.println(s);
			 if(s.contains("latest_assembly_versions")){
//				System.err.println("Looking at '"+s+"'");
				 found+=examineAssemblies(s, tsw, speciesName);
			}
		}
		if(found>0){return found;}
		for(String s : contents){
//			System.err.println(s);
			if(s.contains("all_assembly_versions")){
//				System.err.println("Looking at '"+s+"'");
				found+=examineAssemblies(s, tsw, speciesName);
			}
		}
		return found;
	}
	
	static int examineAssemblies(String baseAddress, TextStreamWriter tsw, String speciesName){
		if(verbose){System.err.println("examineAssemblies: "+baseAddress);}
		ArrayList<String> contents=ServerTools.listDirectory(baseAddress, retries);
//		System.err.println("C: "+contents);
		int found=0;
		for(String s : contents){
//			System.err.println(s);
			found+=examineAssembly(s, tsw, speciesName);
			if(found>0){break;}
		}
		return found;
	}
	
	static int examineAssembly(String baseAddress, TextStreamWriter tsw, String speciesName){
		if(verbose){System.err.println("examineAssembly: "+baseAddress);}
		ArrayList<String> contents=ServerTools.listDirectory(baseAddress, retries);
//		System.err.println("D: "+contents);
		String gff=null;
		String fna=null;
		for(String s : contents){
//			System.err.println(s);
			if(!s.contains("_from_genomic")){
				if(s.endsWith("genomic.fna.gz")){fna=s;}
				else if(s.endsWith("genomic.gff.gz")){gff=s;}
			}
		}
		if(fna!=null && gff!=null){
			System.err.println("Printing: "+fna);
//			System.err.println(fna);
			synchronized(tsw){
				if(renameFiles){
					tsw.println("wget -q -O - "+fna+" > "+speciesName+".fna.gz");
					tsw.println("wget -q -O - "+gff+" > "+speciesName+".gff.gz");
				}else{
					tsw.println("wget -q "+fna);
					tsw.println("wget -q "+gff);
				}
				tsw.println();
			}
			return 1;
		}
		return 0;
	}
	
	static String makeSubAddress(String baseAddress, String extension){
		if(!baseAddress.endsWith("/")){baseAddress=baseAddress+"/";}
		String subAddress=baseAddress+extension.substring(extension.indexOf('/')+1);
		return subAddress;
	}
	
	static boolean verbose=true;
	static boolean allowSameGenus=false;
	static boolean renameFiles=true;
	static int retries=99;
	
	static int totalSpecies=0;
	static int totalGenus=0;
	static int totalGenomes=0;

	private static final Integer one=1;
	
}
