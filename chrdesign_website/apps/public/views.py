# Django
from cgitb import reset
from csv import excel
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from .forms import FragmentForm, FragmentFormSet, Form_settings, Form_excel
import bleach

# Requests
import requests
import json

import os
import shutil
# Pandas
import pandas as pd

# Biopython
import primer3
from Bio import SeqIO
from Bio.SeqUtils import GC
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation

#Warnings
import warnings
warnings.filterwarnings('ignore')

# RENDERING FUNCTIONS
def help(request):
    print(request)
    return render(request, 'help.html')

def results(request):
    print(request)
    return render(request, 'results.html')
def results2(request):
    print(request)
    return render(request, 'results2.html')


def index(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        formset = FragmentFormSet()
        form_excel = Form_excel(prefix="form_excel")
        form_settings = Form_settings(prefix="form_settings")
        
    elif request.method == "POST" and 'btnform1' in request.POST:
        formset = FragmentFormSet(request.POST, request.FILES)
        form_excel = Form_excel(request.POST, request.FILES, prefix="form_excel")
        form_settings = Form_settings( request.POST,prefix="form_settings")
        if formset.is_valid() and form_settings.is_valid():
            # Read SHR tags file and save as lists
            df_SHRs = pd.read_excel ('/app/static/DB_files/SHR_tags.xlsx')

            # general primer settings
            GC_min_g = form_settings.cleaned_data.get('GC_min')
            GC_max_g = form_settings.cleaned_data.get('GC_max')
            Ta_min_g = form_settings.cleaned_data.get('Ta_min')
            Ta_max_g = form_settings.cleaned_data.get('Ta_max')
            Tm_dif_g = form_settings.cleaned_data.get('Tm_dif')
            Range_g = form_settings.cleaned_data.get('Range')
            num_fragments = 0
            for form in formset:
                if form not in formset.deleted_forms:
                    num_fragments = num_fragments + 1
            i = -1

            # Create df with Primer DB IMB fields 
            cols_df_primers = ["Primer name", "Sequence 5' to 3'", "Length (ntd)", "Ta (°C)", "Target gene or region", "Purpose"]
            df_primers = pd.DataFrame(columns = cols_df_primers)
            
            # Create an initial empty sequence for the map
            # Create a record
            map_record = SeqRecord("", 
                            id='1234', # random accession number
                            name='SYNCHR',
                            description='Synthetic chromosome')


            # Create df for input summary
            cols_df_input = ["Fragment name",
                                "Start position",
                                'End position',
                                "Genbank file name",
                                #"Existing Fwd primer (5'-3')",
                                #"Existing Rv primer (5'-3')",
                                "Min (GC content)", 
                                "Max (GC content)",
                                "Min (Ta)",
                                "Max (Ta)",
                                "Max (Tm diff)",
                                "Range [Yes/No]"]
            df_input = pd.DataFrame(columns = cols_df_input)

            cols_df_input_settings = ["Min (GC content)",
                    "Max (GC content)",
                    "Min (Ta)",
                    "Max (Ta)",
                    "Max (Tm diff)",
                    "Range [Yes/No]"]
                    #"Polymerase",
                    #"Primer concentration"]
            if Range_g:
                RangeYN = "Yes"
            else:
                RangeYN = "No"
            df_input_settings = pd.DataFrame(columns = cols_df_input_settings)
            df_3 = {"Min (GC content)": GC_min_g, 
            "Max (GC content)":GC_max_g,
            "Min (Ta)":Ta_min_g,
            "Max (Ta)":Ta_max_g,
            "Max (Tm diff)":Tm_dif_g,
            "Range [Yes/No]": RangeYN}
            #"Polymerase": "Phusion",
            #"Primer concentration":0.2}     
                    
            df_input_settings=df_input_settings.append(df_3, ignore_index=True) 
            forms = []
            for form in formset:
                if form not in formset.deleted_forms:  
                    d_form=dict()
                    d_form["name"] = form.cleaned_data.get('name')
                    d_form["start"] = form.cleaned_data.get('start')
                    d_form["end"] = form.cleaned_data.get('end')
                    d_form["gb"] = form.cleaned_data.get('genbank')
                    d_form["ord"] = form.cleaned_data.get('ORDER')
                    d_form["dele"] = form.cleaned_data.get('DETELE')
                    #d_form["seq1"] = form.cleaned_data.get('Seq1')
                    #d_form["seq2"] = form.cleaned_data.get('Seq2')
                    d_form["res"] = form.cleaned_data.get('Restrictions')
                    if form.cleaned_data.get('Restrictions'):
                        d_form["GC_min"] = form.cleaned_data.get('GC_min')
                        d_form["GC_max"] = form.cleaned_data.get('GC_max')
                        d_form["Ta_min"] = form.cleaned_data.get('Ta_min')
                        d_form["Ta_max"] = form.cleaned_data.get('Ta_max')
                        d_form["Tm_dif"] = form.cleaned_data.get('Tm_dif')
                        d_form["Range"] = form.cleaned_data.get('Range')
                    forms.append(d_form)
            ordered_forms = sorted(forms, key=lambda d: d['ord'])    
         
            f_no_success=list()
            flag_no_success = False
            for form in ordered_forms:
                if form not in formset.deleted_forms:
                    i = i + 1
                    name = form["name"]
                    start = form["start"]
                    end = form["end"]
                    gb = form["gb"]
                    handle_uploaded_file(gb)
                    #Seq1 = form["seq1"]
                    #Seq2 = form["seq2"]
                    res = form["res"]
                    if res:
                        GC_min = form["GC_min"]
                        GC_max = form["GC_max"]
                        Ta_min = form["Ta_min"]
                        Ta_max = form["Ta_max"]
                        Tm_dif = form["Tm_dif"]
                        Range  = form["Range"]
                        df_primers, map_record, df_input = primer_calc(start, end, '/app/static/upload/'+gb.name, name, GC_min, GC_max, Ta_min, Ta_max, Tm_dif, Range, i, num_fragments, df_primers, map_record, df_input, res, flag_no_success, df_SHRs)
                        if str(map_record) != "False":
                            pass
                        else:
                            flag_no_success = True


                            

                    else:
                        df_primers, map_record, df_input = primer_calc(start, end, '/app/static/upload/'+gb.name, name, GC_min_g, GC_max_g, Ta_min_g, Ta_max_g, Tm_dif_g, Range_g, i, num_fragments, df_primers, map_record, df_input, res, flag_no_success, df_SHRs)
                        if str(map_record) != "False":
                            pass
                        else:
                            flag_no_success = True


                    #bleach?
            else: # this runs if for-loop ends without breaks
        # else (not valid) is automaticly generated by django

                # Export excel file
                df_primers.to_excel("/app/static/download/Primer_DB.xlsx", index=False)  

                # Export excel file
                with pd.ExcelWriter("/app/static/download/Input.xlsx") as writer:
                    df_input.to_excel(writer, sheet_name='Fragments', index=False)
                    df_input_settings.to_excel(writer, sheet_name="General primer settings",index=False)  

                
                # Export GenBank file
                if not flag_no_success:
                    map_record.annotations["topology"]="circular"
                    map_record.annotations['molecule_type'] = "DNA"
                    output_file = open('/app/static/download/SynChr.gb', 'w')
                    SeqIO.write(map_record, output_file, 'genbank')
                    output_file.close()
                    return redirect("/results")
                else:
                    return redirect("/results2")


    elif request.method == "POST" and 'btnform2' in request.POST:
        # Create df with Primer DB IMB fields 
        cols_df_primers = ["Primer name", "Sequence 5' to 3'", "Length (ntd)", "Ta (°C)", "Target gene or region", "Purpose"]
        df_primers = pd.DataFrame(columns = cols_df_primers)
        
        # Create an initial empty sequence for the map
        # Create a record
        map_record = SeqRecord("", 
                        id='1234', # random accession number
                        name='SYNCHR',
                        description='Synthetic chromosome')


        gbs = request.FILES.getlist('Genbanks')
        formset = FragmentFormSet(request.POST, request.FILES)
        form_excel = Form_excel(request.POST, request.FILES, prefix="form_excel")
        form_settings = Form_settings( request.POST,prefix="form_settings")
        i = -1

        if form_excel.is_valid():
            # Read SHR tags file and save as lists
            df_SHRs = pd.read_excel ('/app/static/DB_files/SHR_tags.xlsx')

            excel_file = form_excel.cleaned_data.get('ExcelFile')
            handle_uploaded_file(excel_file)
            gbs_list=[]
            for gb in gbs:
                handle_uploaded_file(gb)
                gbs_list.append(gb.name)
            df_excel = pd.read_excel ('/app/static/upload/'+excel_file.name)
            df_excel_settings = pd.read_excel ('/app/static/upload/'+excel_file.name, sheet_name="General primer settings")
            GC_min_g = df_excel_settings['Min (GC content)'][0]
            GC_max_g = df_excel_settings['Max (GC content)'][0]
            Ta_min_g = df_excel_settings['Min (Ta)'][0]
            Ta_max_g = df_excel_settings['Max (Ta)'][0]
            Tm_dif_g = df_excel_settings['Max (Tm diff)'][0]
            Range_g  = df_excel_settings['Range [Yes/No]'][0]


            num_fragments = 0
            for ind in df_excel.index:
                num_fragments = num_fragments + 1
            
            flag_no_success = False
            for ind in df_excel.index:
                i = i + 1
                name = df_excel['Fragment name'][ind]
                start = df_excel['Start position'][ind]
                end = df_excel['End position'][ind]
                gb = df_excel['Genbank file name'][ind]

                if gb not in gbs_list:
                    return render(request, 'index.html', {"form":formset, "form1":form_settings, "form2":form_excel, "success": True})

                GC_min = df_excel['Min (GC content)'][ind]
                GC_max = df_excel['Max (GC content)'][ind]
                Ta_min = df_excel['Min (Ta)'][ind]
                Ta_max = df_excel['Max (Ta)'][ind]
                Tm_dif = df_excel['Max (Tm diff)'][ind]
                Range  = df_excel['Range [Yes/No]'][ind]
                if GC_min == "" or pd.isnull(GC_min):
                    GC_min = GC_min_g
                if GC_max == "" or pd.isnull(GC_max):
                    GC_max = GC_max_g
                if Ta_min == "" or pd.isnull(Ta_min):
                    Ta_min = Ta_min_g
                if Ta_max == "" or pd.isnull(Ta_max):
                    Ta_max = Ta_max_g
                if Tm_dif == "" or pd.isnull(Tm_dif):
                    Tm_dif = Tm_dif_g
                if Range == "" or pd.isnull(Range):
                    Range = Range_g    
                df_primers, map_record, df_input = primer_calc(start, end, '/app/static/upload/'+gb, name, GC_min, GC_max, Ta_min, Ta_max, Tm_dif, Range, i, num_fragments, df_primers, map_record, 0, 0, flag_no_success, df_SHRs)
                if str(map_record) != "False":
                    pass
                else:
                    flag_no_success = True

            # Export excel file
            df_primers.to_excel("/app/static/download/Primer_DB.xlsx", index=False)  

            # Rename Input file
            src = r'/app/static/upload/'+excel_file.name
            dst = r'/app/static/download/'+excel_file.name

            shutil.copyfile(src, dst)

            os.rename(r'/app/static/download/'+excel_file.name,r'/app/static/download/Input.xlsx' )
            
            # Export GenBank file
            if not flag_no_success:
                map_record.annotations["topology"]="circular"
                map_record.annotations['molecule_type'] = "DNA"
                output_file = open('/app/static/download/SynChr.gb', 'w')
                SeqIO.write(map_record, output_file, 'genbank')
                output_file.close()
                

                return redirect("/results")
            else:
                return redirect("/results2")


    else:
        raise NotImplementedError

    return render(request, 'index.html', {"formset":formset , "form1":form_settings, "form2":form_excel})



# FUNCTIONS
def handle_uploaded_file(f):  
    with open('/app/static/upload/'+f.name, 'wb+') as destination:  
        for chunk in f.chunks():  
            destination.write(chunk)  






def primer_calc(start_user, end_user, file, name, GC_min, GC_max, Ta_min, Ta_max, Tm_dif, RangeTF, i, num_fragments, df_primers, map_record, df_input, res, flag_no_success, df_SHRs):
    frag_name = name
    print(frag_name)
    start_user = start_user-1 # real start
    end_user = end_user
    i = i
    num_frags = num_fragments
    conc_primers="0.2"

    for seq_record in SeqIO.parse(file, "genbank"):  
        seq_record=seq_record
        len_template = len(seq_record)   
    if seq_record.annotations["topology"] == "linear":
        linear = True
    else:
        linear= False
    
    # Restrictions
    GC_max = GC_max # Maximum GC% content
    GC_min = GC_min # Minimum GC% content
    Tm_dif = Tm_dif  # Temperature difference between FW and RV primers
    Ta_max = Ta_max # Maximum annealing temperature
    Ta_min = Ta_min # Minimum annealing temperature
    p3_end = ("g","c") # 3'end has to be g or c
    try:
        RangeTF=RangeTF.lower()
    except:
        pass
    if RangeTF == True or RangeTF == "yes":
        RangeYN= "Yes"
        if not linear:
            Range = 100  # Search in a range of 100 nucleotides before and after the fragment
                        # Do this if primers that meet the conditions cannot be found within the specified start and end positions.
                        # Start  adding nucleotide by nucleotide
        else:
            if start_user-100<0:
                Range_FW = start_user
            else:
                Range_FW = 100
            if end_user + 100 > len_template:
                Range_RV = len_template-end_user
            else:
                Range_RV = 100
            if Range_FW <Range_RV:
                Range = Range_FW
            else:
                Range = Range_RV

    else:
        RangeYN= "No"
        Range = 0


    Flag_Range, i_FW_range, i_RV_range = True, 0, 0
    while Flag_Range == True:
        start = start_user-i_FW_range
        end = end_user+i_RV_range
        nt_len_list = [20, 21, 22, 23, 19, 18, 24, 25, 26, 27, 28, 29, 30] # Number of nucleotides in : start looking into length 20 and if it is not a good primer continue in the list
        Flag=True
        Flag_FW, i_FW = False, -1
        Flag_RV, i_RV = False, -1
        while Flag==True:  
            if Flag_FW == False:
                i_FW=i_FW+1
                nt_FW = nt_len_list[i_FW]
                if (len_template-start)<nt_FW:
                    Seq_FW=str(seq_record.seq[start:]+seq_record.seq[:nt_FW-(len_template-start)]).lower()
                else:
                    Seq_FW=str(seq_record.seq[start:start+nt_FW]).lower()
                if start != 0 :
                    bef_FW = str(seq_record.seq[start-1:start]).upper()
                else:
                    if not linear:
                        bef_FW = str(seq_record.seq[-1:]).upper()
                    else:
                        bef_FW = "x"
                z = -1
                bef_FW_str = str()
                while bef_FW == df_SHRs.iat[i,2][z]:
                    start = start - 1
                    z= z-1
                    bef_FW_str = bef_FW + bef_FW_str 
                    if start != 0 :
                        bef_FW = str(seq_record.seq[start-1:start]).upper()
                    else:
                        if not linear:
                            bef_FW = str(seq_record.seq[-1:]).upper()
                        else:
                            bef_FW = "x"
                if bef_FW_str != "":
                    Seq_FW_tc = bef_FW_str + Seq_FW
                
                else:
                    Seq_FW_tc = Seq_FW
                len_SHR_FW = len(bef_FW_str)


                # Check for CG content [40-60 %] and G/C in 3'
                if GC(Seq_FW_tc)>=GC_min and \
                GC(Seq_FW_tc)<=GC_max and \
                (Seq_FW_tc[-1] in p3_end):
                    Flag_FW = True
                # RV primer
            if Flag_RV == False:
                i_RV=i_RV+1
                nt_RV = nt_len_list[i_RV]
                if end<nt_RV:
                    Seq_RV=str((seq_record.seq[len_template+end-nt_RV:]+seq_record.seq[:end]).reverse_complement()).lower()

                else:
                    Seq_RV=str(seq_record.seq[end-nt_RV:end].reverse_complement()).lower()
                
                if end != len_template :
                    af_RV = str(seq_record.seq[end:end+1].reverse_complement()).upper()
                else:
                    if not linear:
                        af_RV = str(seq_record.seq[:1].reverse_complement()).upper()
                    else:
                        af_RV = "x"

                if i == num_frags-1:
                    SHR_RV = df_SHRs.iat[0,3]
                else:
                    SHR_RV = df_SHRs.iat[i+1,3]

                z = -1
                af_RV_str = str()
                while af_RV == SHR_RV[z]:
                    end = end + 1
                    z= z-1
                    af_RV_str = af_RV + af_RV_str 
                    if end != len_template :
                        af_RV = str(seq_record.seq[end:end+1].reverse_complement()).upper()
                    else:
                        if not linear:
                            af_RV = str(seq_record.seq[:1].reverse_complement()).upper()
                        else:
                            af_RV = "x"
                if af_RV_str != "":
                    Seq_RV_tc = af_RV_str + Seq_RV
                    
                else:
                    Seq_RV_tc = Seq_RV
                len_SHR_RV = len(af_RV_str)



                # Check for CG content [40-60 %] and G/C in 3'
                if GC(Seq_RV_tc)>=GC_min and \
                GC(Seq_RV_tc)<=GC_max and \
                (Seq_RV_tc[-1] in p3_end):
                    Flag_RV = True

            if Flag_FW == True and Flag_RV == True:
            # Web access to extract Ta
                URL='https://tmapi.neb.com/tm?seq1='+Seq_FW_tc+'&seq2='+Seq_RV_tc+'&conc='+conc_primers+'&prodcode=phusion-0&email=tmapi@neb.com'
                resp = requests.get(URL)
                resp_dict=json.loads(resp.text)
                Ta,Tm_FW, Tm_RV = resp_dict['data']['ta'],resp_dict['data']['tm1'],resp_dict['data']['tm2']
                FW_homo = primer3.calcHomodimer(Seq_FW_tc).dg/1000
                RV_homo = primer3.calcHomodimer(Seq_RV_tc).dg/1000
                hetero = primer3.calcHeterodimer(Seq_FW_tc,Seq_RV_tc).dg/1000
                #print(frag_name, Seq_FW_tc, primer3.calcHomodimer(Seq_FW_tc).dg/1000)
                #print(Seq_RV_tc, primer3.calcHomodimer(Seq_RV_tc).dg/1000) 
                #print(primer3.calcHeterodimer(Seq_FW_tc,Seq_RV_tc).dg/1000)      
                if Ta>=Ta_min and Ta<=Ta_max and\
                    FW_homo >= -12 and RV_homo >= -12 and hetero >= -12 and\
                    abs(Tm_FW-Tm_RV)<=Tm_dif:
                        #print(frag_name, FW_homo, RV_homo, hetero)
                        Flag_Range=False
                       # Primer name and SHR addition
                        SHR_seq_FW = df_SHRs.iat[i,2] + Seq_FW.lower()
                        Primer_name_FW=str(df_SHRs.iat[i,0])+'_'+frag_name+'_FW'
                        if i == num_frags-1:
                            SHR_seq_RV = df_SHRs.iat[0,3] + Seq_RV.lower()
                            Primer_name_RV=str(df_SHRs.iat[0,0])+'_'+frag_name+'_RV'
                        else:
                            SHR_seq_RV = df_SHRs.iat[i+1,3] + Seq_RV.lower()
                            Primer_name_RV=str(df_SHRs.iat[i+1,0])+'_'+frag_name+'_RV'

                       # Primer name and SHR addition
                        # SHR_FW = SHRs_FW[0]
                        # if i == num_frags-1:
                        #     print("last fragment")
                        #     SHR_seq_FW = SHR_FW + Seq_FW.lower()
                        #     Primer_name_FW=str(SHRs_FW_names[0])+'_'+str(frag_name)+'_FW'
                        #     SHR_RV = SHRs_RV[0]
                        #     SHR_seq_RV = SHRs_RV[0] + Seq_RV.lower()
                        #     Primer_name_RV=str(SHRs_RV_names[0])+'_'+str(frag_name)+'_RV'
                        # else:
                        #     SHR_RV = SHRs_RV[1]
                        #     while_i = 0

                        #     while SHR_FW[-1].lower() == bef_FW or SHR_RV[-1].lower() == af_RV:
                        #         print(SHR_FW, bef_FW)
                        #         print(SHR_RV, af_RV)
                        #         while_i = while_i + 1
                        #         SHR_FW = SHRs_FW[while_i]
                        #         SHR_RV = SHRs_RV[while_i+1]

                        #     print(SHR_FW, bef_FW)
                        #     print(SHR_RV, af_RV)


                        #     SHR_seq_FW = SHR_FW + Seq_FW.lower()
                        #     Primer_name_FW=str(SHRs_FW_names[while_i])+'_'+str(frag_name)+'_FW'

                        #     SHR_seq_RV = SHRs_RV[while_i+1] + Seq_RV.lower()
                        #     Primer_name_RV=str(SHRs_RV_names[while_i+1])+'_'+str(frag_name)+'_RV'
                            
                        #     SHRs_FW.pop(while_i)
                        #     SHRs_RV.pop(while_i)
                        #     SHRs_FW_names.pop(while_i)
                        #     SHRs_RV_names.pop(while_i+1)
                        #     print(SHRs_FW_names, SHRs_RV_names)



                        # Enter excel primer fields 
                        # FW primer
                        data_FW = {'Primer name':Primer_name_FW,
                                "Sequence 5' to 3'":SHR_seq_FW,
                                'Length (ntd)':len(SHR_seq_FW),
                                "Ta (°C)": Ta,
                                "Target gene or region": frag_name, 
                                "Purpose":'Synthetic chromosome construction'}              
                        # RV primer
                        data_RV = {'Primer name':Primer_name_RV,
                                "Sequence 5' to 3'":SHR_seq_RV,
                                'Length (ntd)':len(SHR_seq_RV),
                                "Ta (°C)": Ta,
                                "Target gene or region": frag_name, 
                                "Purpose":'Synthetic chromosome construction'}  
                        # Add FW and RV primers for this fragment to df_primer

                        df_primers=df_primers.append(data_FW, ignore_index=True)
                        df_primers=df_primers.append(data_RV, ignore_index=True)

                        if isinstance(df_input, pd.DataFrame):
                            if res:
                                df2 = {'Fragment name':name,
                                    "Start position":start_user+1,
                                    'End position':end_user,
                                    "Genbank file name": os.path.basename(file),
                                    #"Existing Fwd primer (5'-3')":"",
                                    #"Existing Rv primer (5'-3')":"",
                                    "Min (GC content)": GC_min, 
                                    "Max (GC content)":GC_max,
                                    "Min (Ta)":Ta_min,
                                    "Max (Ta)":Ta_max,
                                    "Max (Tm diff)":Tm_dif,
                                    "Range [Yes/No]":RangeYN} 
                            else:
                                df2 = {'Fragment name':name,
                                    "Start position":start_user+1,
                                    'End position':end_user,
                                    "Genbank file name": os.path.basename(file),
                                    #"Existing Fwd primer (5'-3')":"",
                                    #"Existing Rv primer (5'-3')":"",
                                    "Min (GC content)": "", 
                                    "Max (GC content)":"",
                                    "Min (Ta)":"",
                                    "Max (Ta)":"",
                                    "Max (Tm diff)":"",
                                    "Range [Yes/No]":""}                            
                            df_input=df_input.append(df2, ignore_index=True)

                        # MAP GENERATION
                        # Add FW SHR and fragment sequence to existing map record
                        if not flag_no_success:
                            SHR_record = SeqRecord(Seq(df_SHRs.iat[i,2]), 
                                            id='1', # random accession number
                                            name='SHR',
                                            description='SHR')
                            if start>end:
                                map_record = map_record + SHR_record + seq_record[start+len_SHR_FW:]+seq_record[:end-len_SHR_RV]
                            else:
                                map_record = map_record + SHR_record + seq_record[start+len_SHR_FW:end-len_SHR_RV]                         
                            return(df_primers, map_record, df_input)
                        else:
                            return(df_primers, False, df_input)

                #else:
                if i_FW <= i_RV: 
                    Flag_FW=False
                else:
                    Flag_RV=False
            if (nt_FW == 30 and nt_RV==30):
                i_FW_range+=1
                i_RV_range+=1     
                break
            if nt_FW == 30 and Flag_FW == False:
                i_FW_range+=1
                break
            if nt_RV == 30 and Flag_RV == False: 
                i_RV_range+=1
                break

        if i_FW_range>Range or i_RV_range> Range:
            # Enter excel primer fields 
            # FW primer
            data_FW = {'Primer name':"Fragment "+str(i+1)+": "+str(frag_name),
                    "Sequence 5' to 3'":"Not found",
                    'Length (ntd)':"",
                    "Ta (°C)": "",
                    "Target gene or region": frag_name, 
                    "Purpose":''}              
            # RV primer
            data_RV = {'Primer name':"Fragment "+str(i+1)+": "+str(frag_name),
                    "Sequence 5' to 3'":"Not found",
                    'Length (ntd)':"",
                    "Ta (°C)": "",
                    "Target gene or region": frag_name, 
                    "Purpose":""}  
            # Add FW and RV primers for this fragment to df_primer

            df_primers=df_primers.append(data_FW, ignore_index=True)
            df_primers=df_primers.append(data_RV, ignore_index=True)
            if isinstance(df_input, pd.DataFrame):
                if res:
                    df2 = {'Fragment name':name,
                        "Start position":start_user+1,
                        'End position':end_user,
                        "Genbank file name": os.path.basename(file),
                        #"Existing Fwd primer (5'-3')":"",
                        #"Existing Rv primer (5'-3')":"",
                        "Min (GC content)": GC_min, 
                        "Max (GC content)":GC_max,
                        "Min (Ta)":Ta_min,
                        "Max (Ta)":Ta_max,
                        "Max (Tm diff)":Tm_dif,
                        "Range [Yes/No]":RangeYN} 
                else:
                    df2 = {'Fragment name':name,
                        "Start position":start_user+1,
                        'End position':end_user,
                        "Genbank file name": os.path.basename(file),
                        #"Existing Fwd primer (5'-3')":"",
                        #"Existing Rv primer (5'-3')":"",
                        "Min (GC content)": "", 
                        "Max (GC content)":"",
                        "Min (Ta)":"",
                        "Max (Ta)":"",
                        "Max (Tm diff)":"",
                        "Range [Yes/No]":""}                            
                df_input=df_input.append(df2, ignore_index=True)
            return df_primers, False, df_input

