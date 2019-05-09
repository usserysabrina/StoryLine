
import simplenlg.framework.*;
import simplenlg.lexicon.*;
import simplenlg.realiser.english.*;
import simplenlg.phrasespec.*;
import simplenlg.features.*;


/*package simplenlg.syntax.english;*/
/*import java.util.Arrays;*/

import simplenlg.features.Feature;
import simplenlg.features.Tense;
import simplenlg.framework.CoordinatedPhraseElement;
import simplenlg.framework.DocumentElement;
import simplenlg.framework.NLGElement;
import simplenlg.framework.NLGFactory;
import simplenlg.lexicon.Lexicon;
import simplenlg.phrasespec.NPPhraseSpec;
import simplenlg.phrasespec.PPPhraseSpec;
import simplenlg.phrasespec.SPhraseSpec;
import simplenlg.phrasespec.VPPhraseSpec;
import simplenlg.realiser.english.Realiser;

import java.io.File;
import java.io.IOException;
import java.util.*;
import java.io.BufferedReader;
import java.io.InputStreamReader;

import jxl.Cell;
import jxl.Sheet;
import jxl.Workbook;

import jxl.read.biff.BiffException;

import jxl.write.Label;
import jxl.write.Number;
import jxl.write.WritableSheet;
import jxl.write.WritableWorkbook;
import jxl.write.WriteException;
import jxl.write.*;

import java.util.ArrayList;
import jxl.Cell;
import jxl.LabelCell;
import jxl.NumberCell;

public class SimpleNLG 
{
	
	
	public static void main(String[] args)
	  throws BiffException, IOException, WriteException
	{
		Workbook workbook = Workbook.getWorkbook(new File("StoryLine_to_SimpleNLG.xls"));
        Sheet sheet = workbook.getSheet(0);
		
		WritableWorkbook workbookz;
		workbookz = Workbook.createWorkbook(new File("SimpleNLG_Outputs.xls"));
        WritableSheet sheetz = workbookz.createSheet("StoryLine Revised US", 0);
				
			
		ArrayList<String> getUSID=new ArrayList<String>();
		ArrayList<String> getRole=new ArrayList<String>();
		ArrayList<String> getBenefit=new ArrayList<String>();
		ArrayList<String> getSubject=new ArrayList<String>();
		ArrayList<String> getActionPhrase=new ArrayList<String>();
		ArrayList<String> getPrepPhrase=new ArrayList<String>();
		ArrayList<String> getAdverbPhrase=new ArrayList<String>();
		
	
	/* Reading POS from outputs of Python for input into SimpleNLG*/
	/*first row is a header row so can be ignored*/
	
		for (int row = 0 ; row < sheet.getRows(); row ++ ) {
			getUSID.add(sheet.getCell(0, row).getContents());
		 	getRole.add(sheet.getCell(1, row).getContents());
			getBenefit.add(sheet.getCell(2, row).getContents());
			getSubject.add(sheet.getCell(3, row).getContents());
			getActionPhrase.add(sheet.getCell(4, row).getContents());
			getPrepPhrase.add(sheet.getCell(5, row).getContents());
			getAdverbPhrase.add(sheet.getCell(6, row).getContents());
								
		  }
		  
		/*converting inputs to arrays for iteration purposes*/
		String[] arr_USID = getUSID.toArray(new String[getUSID.size()]);
		arr_USID = getUSID.toArray(arr_USID);
				  
		String[] arr_role = getRole.toArray(new String[getRole.size()]);
		arr_role = getRole.toArray(arr_role);
		
		String[] arr_benefit = getBenefit.toArray(new String[getBenefit.size()]);
		arr_benefit = getBenefit.toArray(arr_benefit);
		
		String[] arr_subj = getSubject.toArray(new String[getSubject.size()]);
		arr_subj = getSubject.toArray(arr_subj);
			
		String[] arr_actionphrase = getActionPhrase.toArray(new String[getActionPhrase.size()]);
		arr_actionphrase = getActionPhrase.toArray(arr_actionphrase);
				
		String[] arr_prep = getPrepPhrase.toArray(new String[getPrepPhrase.size()]);
		arr_prep = getPrepPhrase.toArray(arr_prep);
		
		String[] arr_adverb = getAdverbPhrase.toArray(new String[getAdverbPhrase.size()]);
		arr_adverb = getAdverbPhrase.toArray(arr_adverb);
			
			
		Lexicon lexicon = Lexicon.getDefaultLexicon();                         
		NLGFactory nlgFactory = new NLGFactory(lexicon);             
		Realiser r = new Realiser(lexicon);
	
		for (int row = 0 ; row < sheet.getRows(); row ++ ) {
			
			/*User Story template: "As a <role>, I want to <action>, so that <benefit>"
			# Output = Role phrase +  <SimpleNLG outputs> + benefit phrase"*/
			/* where <SimpleNLG outputs = subject + action phrase + prepositional phrases + adverb phrase.*/
			
			NPPhraseSpec subject = nlgFactory.createNounPhrase(arr_subj[row]);
			VPPhraseSpec verb = nlgFactory.createVerbPhrase(arr_actionphrase[row]);
			/*NPPhraseSpec object = nlgFactory.createNounPhrase(arr_nounobjectphrase[row]);*/
			SPhraseSpec p = nlgFactory.createClause(subject, verb);
			if (!arr_prep[row].isEmpty())
				p.addComplement(arr_prep[row]);
			if (!arr_adverb[row].isEmpty()) 
				p.addComplement(arr_adverb[row]);
			
			String output_action = r.realiseSentence(p);
			String output_action_revised =  output_action.substring(0, output_action.length() - 1);
			
			String output_US = arr_role[row] + ", " + output_action_revised + ", " + arr_benefit[row] +".";
			String output_US_clean0 = output_US.replace(" s ", "'s ");
			String output_US_clean1 = output_US_clean0.replace(" .", ".");
			String output_US_clean2 = output_US_clean1.replace(" ,", ",");
			/*System.out.println(output_US);
		
			/*write to outputs file for user (next steps)*/
	
			try {
			Label Column0 = new Label(0,0, "US_ID");
			Label Column1 = new Label(1,0, "StoryLine Revised US");
			Label label0 = new Label(0,row, arr_USID[row]);
            Label label1 = new Label(1,row, output_US_clean2);
            sheetz.addCell(label0);
			sheetz.addCell(label1);
			sheetz.addCell(Column0); 
			sheetz.addCell(Column1);
			} catch (Exception e) {
            e.printStackTrace();
			}
		}
			workbookz.write();
			workbookz.close();
			
			/*initialize StoryLine again to calculate semantic similarity and create QFD file*/
			
			try {
			  String line;
			  Process p = Runtime.getRuntime().exec("python Pairwise_SemSim.py");
			  p.waitFor();
			  /*System.out.println(p.exitValue());*/
			}
			catch (Exception err) {
			  err.printStackTrace();
			}
			
								
	}
	

}


