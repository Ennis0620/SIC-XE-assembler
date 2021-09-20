
#格式1
opcode_one={"FIX":"C4","FLOAT":"C0","HIO":"F4","NORM":"C8","SIO":"F0","TIO":"F8"}
#格式2
opcode_two={"ADDR":"90","CLEAR":"B4","COMPR":"A0","DIVR":"9C","MULR":"98","RMO":"AC","SHIFTL":"A4",
            "SHIFTR":"A8","SUBR":"94","SVC":"B0","TIXR":"B8"}    
#格式3/4
opcode_three_four={"ADD":"18","ADDF":"58","AND":"40","COMP":"28","COMPF":"88","DIV":"24","DIVF":"64",
                   "J":"3C","JEQ":"30","JGT":"34","JLT":"38","JSUB":"48","LDA":"00","LDB":"68","LDCH":"50",
                   "LDF":"70","LDL":"08","LDS":"6C","LDT":"74","LDX":"04","LPS":"D0","MUL":"20","MULF":"60",
                   "OR":"44","RD":"D8","RSUB":"4C","SSK":"EC","STA":"0C","STB":"78","STCH":"54","STF":"80",
                   "STI":"D4","STL":"14","STS":"7C","STSW":"E8","STT":"84","STX":"10","SUB":"1C",
                   "SUBF":"5C","TD":"E0","TIX":"2C","WD":"DC"}

#暫存器碼
register_number = {"A":"0","X":"1","L":"2","PC":"8","SW":"9","B":"3","S":"4","T":"5","F":"6"}

#虛指令判斷
def directive(col):
    if(col=="START"):
        return "START"
    elif(col == "BASE"):
        return "BASE"
    elif(col == "BYTE"):
        return "BYTE"
    elif(col == "WORD"):
        return "WORD"
    elif(col == "RESW"):
        return "RESW"
    elif(col == "RESB"):
        return "RESB"
    elif(col == "END"):
        return "END"
    else:
        return False
#檔案讀取
def read_file(data_name,arr = []):
    with open(data_name,"r",encoding="utf-8-sig") as fp:
        row = fp.readlines()
        for index_row,line in enumerate(row):
            line_strip = line.strip("\n")
            line_split = line_strip.split()
            #動態增加行數
            arr.append([])
            #取出分割後一個一個的字串
            for index,row_per in enumerate(line_split):
                #根據所在行數 動態新增 所分割後得到的字串            
                arr[index_row].append(row_per)
    fp.close()
#重新整合
def reshape_arr(one_d_arr=[],re_arr=[],arr=[[]]):
    #先將全部的指令存到一個新的1維陣列
    for index_row,row in enumerate(arr):
        #如果row裡面有值 且="." 代表是註解不用理他
        if(len(row)>0):
            if(row[0]=="."):
                continue                  
        for index_col,col in enumerate(row):           
            if(col=="RSUB"):
                one_d_arr.append(col)
                one_d_arr.append("")
            else:
                one_d_arr.append(col)    
            
    
    for index,per in enumerate(one_d_arr):
        #為了讓 opcode前面有+號的也能夠讀進去
        per = per.strip('+')   
        #如果讀到的字串 是虛指令或是有在opcode_dic中的指令
        if(directive(per)!=False or per in opcode_one or per in opcode_two or per in opcode_three_four):
            
            now_per = one_d_arr[index]
            next_per = one_d_arr[index+1]
            #如果現在是RSUB，則指將其陣列改為0 ， 因為RSUB沒有運算元
            if(now_per == "RSUB"):
                one_d_arr[index]='0'
            #其餘的都有運算元，所以將本身和下一個改成0
            else:
                one_d_arr[index]='0'
                one_d_arr[index+1]='0'
            
            #當目前的前一個不為0時，代表是symbol
            if(one_d_arr[index-1]!='0'):  
                #RSUB因沒運算元 所以 append 0,RSUB,0
                if(now_per == "RSUB"):
                    re_arr.append(['',now_per,''])
                # symbol(上一個)、當前、下一個 一起append
                else:            
                    re_arr.append([one_d_arr[index-1],now_per,next_per])
            #其他代表沒有symbol
            else:
                re_arr.append(["",now_per,next_per])
 
#計算虛指令要加多少loc
def directive_loc(Loc_int,index_row,index_col,re_arr=[[]]):
    if(re_arr[index_row][index_col]=="BYTE"):
        BYTE_s = re_arr[index_row][index_col+1].split("’")
        if(BYTE_s[0]=="X"):
            Loc_int=1            
            return Loc_int
        elif(BYTE_s[0]=="C"):
            Loc_int = len(BYTE_s[1])
            return Loc_int
    elif(re_arr[index_row][index_col]=="BASE"):
        Loc_int=0
        return Loc_int
    elif(re_arr[index_row][index_col]=="WORD"):
        Loc_int=3
        return Loc_int
    elif(re_arr[index_row][index_col]=="RESW"):
        RESW_add = int(re_arr[index_row][index_col+1])*3
        Loc_int= RESW_add
        return Loc_int
    elif(re_arr[index_row][index_col]=="RESB"):
        RESB_add = int(re_arr[index_row][index_col+1])
        #轉成16進位
        RESB_add_hex = hex(RESB_add)
        #把16進位從str轉成int 讓其可以相加
        Loc_int=int(RESB_add_hex,base=16)
        return Loc_int
    else:
        return "None"

#計算loc位置
def loc_count(Loc_int,re_arr=[[]]):
    START = False
    for index_row,row in enumerate(re_arr):
        for index_col,col in enumerate(row):
            #如果分割後長度=2 代表前面有+ 是第4種格式
            col_add = col.split('+')
            #START指令 代表 其後面是程式指令的開始
            if(col=="START"):
                #強制轉成16進位
                Loc = "0x" + re_arr[index_row][index_col+1]
                Loc_int = int(Loc,base=16)
            #判斷在FIRST後面才要加上START的數值
            elif(col=="FIRST" and START==False):
                re_arr[index_row].append(hex(Loc_int)[2:].upper().zfill(4))
                Loc = hex(Loc_int)
                if(re_arr[index_row][index_col+1] in opcode_one):
                    Loc_int += 1
                elif(re_arr[index_row][index_col+1] in opcode_two):
                    Loc_int += 2
                elif(re_arr[index_row][index_col+1] in opcode_three_four):
                    Loc_int += 3
                elif(len(re_arr[index_row][index_col+1].split('+'))==2 and re_arr[index_row][index_col+1].split('+')[1] in opcode_three_four):
                    Loc_int += 4
                START=True
            elif(START==True and re_arr[index_row][0]!="FIRST"):
                if(directive_loc(Loc_int,index_row,index_col,re_arr)!="None"):
                    #為了讓每行都有4個值 當=BASE 也添加 但添加空白
                    if(col=="BASE"):
                        re_arr[index_row].append("")
                        Loc_int += directive_loc(Loc_int,index_row,index_col,re_arr)
                    else:
                        re_arr[index_row].append(hex(Loc_int)[2:].upper().zfill(4))
                        Loc_int += directive_loc(Loc_int,index_row,index_col,re_arr)              
                #END    
                elif(col=="END"):
                    re_arr[index_row].append(hex(Loc_int)[2:].upper().zfill(4))
                elif(col in opcode_one):
                    
                    re_arr[index_row].append(hex(Loc_int)[2:].upper().zfill(4))
                    Loc = hex(Loc_int)
                    Loc_int += 1
                elif(col in opcode_two):
                    
                    re_arr[index_row].append(hex(Loc_int)[2:].upper().zfill(4))
                    Loc = hex(Loc_int)
                    Loc_int += 2
                elif(col in opcode_three_four):
                    re_arr[index_row].append(hex(Loc_int)[2:].upper().zfill(4))
                    Loc = hex(Loc_int)
                    Loc_int += 3
                elif(len(col_add)==2 and col_add[1] in opcode_three_four):
                    re_arr[index_row].append(hex(Loc_int)[2:].upper().zfill(4))
                    Loc = hex(Loc_int)
                    Loc_int += 4
                
#找symbol
def symbol_lookup(re_arr=[[]]):
    for index_row,row in enumerate(re_arr):
        #找一行的長度>=4 (避免第一行進去)
        if(len(re_arr[index_row])>=4 and re_arr[index_row][0]!=""):
            #symbol
            key = re_arr[index_row][0]
            #loction值
            value = re_arr[index_row][3]
            symbol.setdefault(key,value)          
#opcode 和 nixbpe前兩位 的轉換
def opcode_nixbpe(opcode_value,nixbpe_per2,nixbpe_bef4):

    return_opject_code=""
    
    #先轉為str 再取出 opcode_value後面的數值
    str_opcode_value = str(opcode_value)   #先轉成字串
    opcode_value_beh = str_opcode_value[1] #取得 opcode的個位數 Ex: opcode=5E 就是取 E
    opcode_value_beh_ten = int(opcode_value_beh,base=16) #轉成10進位
    nixbpe_per2_ten = int(nixbpe_per2,base=2) #nixbpe的前兩位二元數字 轉成10進位
    sum_nixbpe_per_opcode_value_beh = nixbpe_per2_ten + opcode_value_beh_ten #相加後得到 10進位的結果
    return_opject_code += str_opcode_value[0] + hex(sum_nixbpe_per_opcode_value_beh)[2:].upper() + hex((int(nixbpe_bef4,base=2)))[2:].upper() 
    return return_opject_code


#計算個別型態的數值
#opm
def count_opm(opcode,opcode_value,pc,TA,B):    
    return_opject_code=""       
    #RSUB沒有運算元
    if(opcode!="RSUB"):
        #找到該key值之value
        TA_value = symbol[TA]
        disp = int("0x"+TA_value,base=16) -  int("0x"+pc,base=16)
        #如果轉成16進位的數字超過3個 代表PC相對不能用 要用基底(BASE)相對
        if(len(hex(abs(disp))[2:])<=3):
            #PC相對的objeetcode前三碼
            return_opject_code+= opcode_nixbpe(opcode_value,"0b11","0b0010")
            if(disp<0):
                two_plus = "0x1000"
                two_plus = int(two_plus,base=16)
                two_plus = two_plus + disp 
                disp_hex = hex(two_plus)[2:].upper()
                    
                return_opject_code+=disp_hex.zfill(3)
            else:
                disp_hex = hex(disp)[2:].upper()
                return_opject_code+=disp_hex.zfill(3)
            return return_opject_code
        else:
            #利用基底來做判斷
            return_opject_code+= opcode_nixbpe(opcode_value,"0b11","0b0100")
            BASE_ten = int("0x"+B,base=16)
            disp = int("0x"+TA_value,base=16) -  BASE_ten
            if(disp<0):
                two_plus = "0x1000"
                two_plus = int(two_plus,base=16)
                two_plus = two_plus + disp 
                disp_hex = hex(two_plus)[2:].upper()
                return_opject_code+=disp_hex.zfill(3)
            else:
                disp_hex = hex(disp)[2:].upper()
                return_opject_code+=disp_hex.zfill(3)
                
            return return_opject_code
#  op#m
def count_op_hide_m(opcode,opcode_value,pc,TA,B):  
    
    return_opject_code=""
    if(opcode!="RSUB"):
        #找到該key值之value
        TA_value = symbol[TA]
        disp = int("0x"+TA_value,base=16) -  int("0x"+pc,base=16)
        if(len(hex(abs(disp))[2:])<=3):
            #PC相對的objeetcode前三碼
            return_opject_code+= opcode_nixbpe(opcode_value,"0b01","0b0010")
            if(disp<0):
                two_plus = "0x1000"
                two_plus = int(two_plus,base=16)
                two_plus = two_plus + disp 
                disp_hex = hex(two_plus)[2:].upper()
                    
                return_opject_code+=disp_hex.zfill(3)
            else:
                disp_hex = hex(disp)[2:].upper()
                return_opject_code+=disp_hex.zfill(3)
            return return_opject_code
        else:
            #利用基底來做判斷
            return_opject_code+= opcode_nixbpe(opcode_value,"0b01","0b0100")
            BASE_ten = int("0x"+B,base=16)
            disp = int("0x"+TA_value,base=16) -  BASE_ten
            if(disp<0):
                two_plus = "0x1000"
                two_plus = int(two_plus,base=16)
                two_plus = two_plus + disp 
                disp_hex = hex(two_plus)[2:].upper()
                return_opject_code+=disp_hex.zfill(3)
            else:
                disp_hex = hex(disp)[2:].upper()
                return_opject_code+=disp_hex.zfill(3)
                
            return return_opject_code
# op@m
def count_op_mouse_m(opcode,opcode_value,pc,TA,B):
    #print("opcode:",opcode,"opcode_value:",opcode_value,"pc:",pc,"TA:",TA,"B:",B)
    return_opject_code=""
    if(opcode!="RSUB"):
        #找到該key值之value
        TA_value = symbol[TA]
        disp = int("0x"+TA_value,base=16) -  int("0x"+pc,base=16)
        if(len(hex(abs(disp))[2:])<=3):
            #PC相對的objectcode前三碼
            return_opject_code+= opcode_nixbpe(opcode_value,"0b10","0b0010")
            if(disp<0):
                two_plus = "0x1000"
                two_plus = int(two_plus,base=16)
                two_plus = two_plus + disp 
                disp_hex = hex(two_plus)[2:].upper()
                    
                return_opject_code+=disp_hex.zfill(3)
            else:
                disp_hex = hex(disp)[2:].upper()
                return_opject_code+=disp_hex.zfill(3)
            return return_opject_code
        else:
            #利用基底來做判斷
            return_opject_code+= opcode_nixbpe(opcode_value,"0b10","0b0100")
            BASE_ten = int("0x"+B,base=16)
            disp = int("0x"+TA_value,base=16) -  BASE_ten
            if(disp<0):
                two_plus = "0x1000"
                two_plus = int(two_plus,base=16)
                two_plus = two_plus + disp 
                disp_hex = hex(two_plus)[2:].upper()
                return_opject_code+=disp_hex.zfill(3).upper()
            else:
                disp_hex = hex(disp)[2:].upper()
                return_opject_code+=disp_hex.zfill(3).upper()
                
            return return_opject_code
# op#c
def count_op_hide_c(opcode,opcode_value,TA):
    return_opject_code=""
    return_opject_code+= opcode_nixbpe(opcode_value,"0b01","0b0000")
    return_opject_code += hex(int(TA))[2:].zfill(3).upper() #記得 op#c 的 c 是10進位 要轉成16進位
    return return_opject_code
    
# +opm
def count_plus_opm(opcode,opcode_value,TA):
    
    return_opject_code=""
    return_opject_code+= opcode_nixbpe(opcode_value,"0b11","0b0001")
    if(TA.isdigit()==True):
        return_opject_code += hex(int(TA))[2:].zfill(5).upper()  # c>4095 = m 記得要轉成16進位
    else:
        TA_value = symbol[TA]
        return_opject_code += TA_value.zfill(5)
    return return_opject_code
# +op#m
def count_plus_op_hide_m(opcode,opcode_value,TA):
    
    return_opject_code=""
    return_opject_code+= opcode_nixbpe(opcode_value,"0b01","0b0001")
    if(TA.isdigit()==True):
        return_opject_code += hex(int(TA))[2:].zfill(5).upper()  # c>4095 = m 記得要轉成16進位
    else:
        TA_value = symbol[TA]
        return_opject_code += TA_value.zfill(5)
    return return_opject_code
# +op@m
def count_plus_op_mouse_m(opcode,opcode_value,TA):
    return_opject_code=""
    return_opject_code+= opcode_nixbpe(opcode_value,"0b10","0b0001")
    if(TA.isdigit()==True):
        return_opject_code += hex(int(TA))[2:].zfill(5).upper()  # c>4095 = m 記得要轉成16進位
    else:
        TA_value = symbol[TA]
        return_opject_code += TA_value.zfill(5)
    return return_opject_code
#opc
def count_opc(opcode,opcode_value,TA):
    return_opject_code=""
    return_opject_code += opcode_nixbpe(opcode_value,"0b11","0b0000")
    return_opject_code += hex(int(TA))[2:].zfill(3).upper()
    return return_opject_code
# op@c
def count_op_mouse_c(opcode,opcode_value,TA):
    return_opject_code=""
    return_opject_code += opcode_nixbpe(opcode_value,"0b10","0b0000")
    return_opject_code += hex(int(TA))[2:].zfill(3).upper()
    return return_opject_code
 # opm,x
def count_opm_dot_x(opcode,opcode_value,pc,TA,B,X):
    return_opject_code=""
    #因為 為opm,x 代表TA只能有3個位數 若超過0~4095(opc,x) 不會存在 因4096(10) = 1000(16) 所以只要判斷,前的operand
    TA_value = symbol[TA[0]]
    disp = int("0x"+TA_value,base=16) -  int("0x"+pc,base=16) - int(X)
    if(len(hex(abs(disp))[2:])<=3):
        #PC相對的objectcode前三碼
        return_opject_code+= opcode_nixbpe(opcode_value,"0b11","0b1010")
        if(disp<0):
            two_plus = "0x1000"
            two_plus = int(two_plus,base=16)
            two_plus = two_plus + disp 
            disp_hex = hex(two_plus)[2:].upper()
                    
            return_opject_code+=disp_hex.zfill(3)
        else:
            disp_hex = hex(disp)[2:].upper()
            return_opject_code+=disp_hex.zfill(3)
        return return_opject_code
    else:
        #利用基底來做判斷
        return_opject_code+= opcode_nixbpe(opcode_value,"0b11","0b1100")
        BASE_ten = int("0x"+B,base=16)
        disp = int("0x"+TA_value,base=16) -  BASE_ten -int(X)
        if(disp<0):
            two_plus = "0x1000"
            two_plus = int(two_plus,base=16)
            two_plus = two_plus + disp 
            disp_hex = hex(two_plus)[2:].upper()
            return_opject_code+=disp_hex.zfill(3).upper()
        else:
            disp_hex = hex(disp)[2:].upper()
            return_opject_code+=disp_hex.zfill(3).upper()
    return return_opject_code
# opc,x
def count_opc_dot_x(opcode,opcode_value,pc,TA,X):
    return_opject_code=""
    TA_value = int(TA[0])
    disp = TA_value - int(X)
    return_opject_code+= opcode_nixbpe(opcode_value,"0b11","0b1000")
    if(disp<0):
        two_plus = "0x1000"
        two_plus = int(two_plus,base=16)
        two_plus = two_plus + disp 
        disp_hex = hex(two_plus)[2:].upper()
                    
        return_opject_code+=disp_hex.zfill(3)
    else:
        disp_hex = hex(disp)[2:].upper()
        return_opject_code+=disp_hex.zfill(3)
    return return_opject_code
# +opm,x
def count_plus_opm_dot_x(opcode,opcode_value,TA,X):
    return_opject_code=""
    return_opject_code+= opcode_nixbpe(opcode_value,"0b11","0b1001")
    TA_value = symbol[TA[0]]
    addr = int("0x"+TA_value,base=16) - int(X)
    if(addr<0):
        two_plus = "0x1000"
        two_plus = int(two_plus,base=16)
        two_plus = two_plus + addr 
        addr_hex = hex(two_plus)[2:].upper()
                    
        return_opject_code+=addr_hex.zfill(5)
    else:
        addr_hex = hex(addr)[2:].upper()
        return_opject_code+=addr_hex.zfill(5)
    return return_opject_code
    
    
#解析是何種型態
def count_per_object(opcode,pc,TA,B,X):
    #print("opcode:",opcode,"pc:",pc,"TA:",TA,"B:",B)
    return_opject_code=""
    #先進行opcode的解析
    op_type=""
    opcode_value=""
    opcode_split = opcode.split("+")
    if(len(opcode_split)==2):
        op_type += "+op"
        opcode_value = opcode_three_four[opcode_split[1]]
        #print(opcode_value)
    else:
        op_type += "op"
        if(opcode in opcode_one):
            #指令格式1就直接回傳opcode就好
            opcode_value = opcode_one[opcode]
            return opcode_value
            #print(opcode_value)
        elif(opcode in opcode_two):
            #指令格式2的較為特殊 只要直接opcode + 暫存器的數值就好
            opcode_value = opcode_two[opcode]
            TA_split_ = TA.split(",")
            if(len(TA_split_)==2):
                first = register_number[TA_split_[0]]
                second = register_number[TA_split_[1]]
                return_opject_code = opcode_value + first + second
                return return_opject_code
            else:
                first = register_number[TA]
                return_opject_code = opcode_value + first + "0"
                return return_opject_code

            #print(return_opject_code)
        elif(opcode in opcode_three_four):
            opcode_value = opcode_three_four[opcode]
            #print(opcode_value)
    
    #接著解析operand
    TA_split_mouse = TA.split("@")
    TA_split_hide = TA.split("#")
    #帶有@
    if(len(TA_split_mouse)==2):
        #判斷符號後面是文字還是數字 還要判斷如果數字大於4095就是m
        if(TA_split_mouse[1].isdigit()==False):
            operand_mouse="@m"
            op_type+=operand_mouse
        else:
            if(int(TA_split_mouse[1])>4095):
                operand_mouse="@m"
                op_type+=operand_mouse
            else:
                operand_mouse="@c"
                op_type+=operand_mouse
    #帶有#        
    if(len(TA_split_hide)==2):
        #判斷符號後面是文字還是數字 還要判斷如果數字大於4095就是m
        if(TA_split_hide[1].isdigit()==False):
            operand_hide="#m"
            op_type+=operand_hide
        else:
            if(int(TA_split_hide[1])>4095):
                operand_hide="#m"
                op_type+=operand_hide
            else:
                operand_hide="#c"
                op_type+=operand_hide
    #沒有特別符號的            
    if(len(TA_split_hide)==1 and len(TA_split_mouse)==1):
        if(TA.isdigit()==False):
            op_type+="m"
        else:
            if(int(TA)>4095):
                op_type+="m"
            else:
                op_type+="c"
    #print(pc,opcode,TA,op_type)
    #TA為BUFFER,X 之類型
    TA_split_dot = TA.split(",")
    if(len(TA_split_dot)==2):
        if(len(opcode_split)==2): #opcode_split 是看有沒有+號
            op_type = "+opm,x"            
        elif(len(opcode_split)!=2):
            if(TA_split_dot[0].isdigit()==True): #若TA_split_dot 第一個為數字=>含要判斷是否大於4095
                if(int(TA_split_dot[0])>4095):
                    op_type = "opm,x"
                else:
                    op_type = "opc,x"
            else:
                op_type = "opm,x"
    
    if(op_type=="opm"):
        ans = count_opm(opcode,opcode_value,pc,TA,B)
        return ans
    elif(op_type=="op#m"):
        ans = count_op_hide_m(opcode,opcode_value,pc,TA_split_hide[1],B)
        return ans
    elif(op_type=="op@m"):
        ans = count_op_mouse_m(opcode,opcode_value,pc,TA_split_mouse[1],B)
        return ans
    elif(op_type=="+opm"):
        ans = count_plus_opm(opcode,opcode_value,TA)
        return ans
    elif(op_type=="op#c"):
        ans = count_op_hide_c(opcode,opcode_value,TA_split_hide[1])
        return ans
    elif(op_type=="+op#m"):
         ans = count_plus_op_hide_m(opcode,opcode_value,TA_split_hide[1])
         return ans
    elif(op_type=="+op@m"):
        ans = count_plus_op_mouse_m(opcode,opcode_value,TA_split_mouse[1])
        return ans
    elif(op_type=="opc"):
        ans = count_opc(opcode,opcode_value,TA)
        return ans
    elif(op_type=="op@c"):
         ans = count_op_mouse_c(opcode,opcode_value,TA_split_mouse[1])
         return ans
    elif(op_type=="opm,x"):
        ans = count_opm_dot_x(opcode,opcode_value,pc,TA_split_dot,B,X)
        return ans
    elif(op_type=="opc,x"):
        ans = count_opc_dot_x(opcode,opcode_value,TA_split_dot,X)
        return ans
    elif(op_type=="+opm,x"):
        ans = count_plus_opm_dot_x(opcode,opcode_value,TA_split_dot,X)
        return ans
#判斷operand 
def operand_def(re_arr=[[]]):
    pc=0 
    B = "0" #基底暫存器BASE的值  
    X = "0" #index先設為0
    for index_row,row in enumerate(re_arr):
        #有CLEAR,代表被清空
        if(row[1]=="CLEAR"):
            if(row[2]=="X"):
                X="0"
        #基底定址
        if(row[1]=="BASE"):
            B = symbol[row[2]]
        #避免START和END傳遞 以及目前是非虛指令
        if(row[1]!="START" and row[1]!="END" and directive(row[1])==False):
         #去檢查指令格式 如過下一個指令位址為空 代表是BASE 所以她上一行的pc 的要跳2行才能找到
            pc = re_arr[index_row+1][3]
            if(pc==''):
                pc = re_arr[index_row+2][3]
                A = count_per_object(row[1],pc,row[2],B,X)
                
            else:
                if(row[1]!="BASE"):
                    A = count_per_object(row[1],pc,row[2],B,X)        
            if(row[1]!="RSUB"):
                #將計算完的object code添加到後面
                row.append(A)
            else:
                row.append("4F0000")
        elif(directive(row[1])!=False):
            if(row[1]=="BYTE"):
                BYTE_s = row[2].split("’")
                if(BYTE_s[0]=="X"):
                    row.append(BYTE_s[1])
                elif(BYTE_s[0]=="C"):
                    sumstr=""
                    for i in BYTE_s[1]:
                        ten_ = ord(i)
                        hex_ = hex(ten_)
                        sumstr+=hex_[2:].upper()
                    row.append(sumstr.upper()) 
                elif(row[1]=="WORD"):
                    ten_WORD = int(row[2])
                    if(ten_WORD<0):
                        #利用補數
                        over_7_digit = "0x"+"1000000"
                        #先轉成10進位的int
                        over_7_digit_hex = int(over_7_digit,base=16)
                        #相加後再轉乘16進位
                        two_plus = over_7_digit_hex + ten_WORD
                        two_plus_hex = hex(two_plus)[2:].upper()
                        row.append(two_plus_hex)
                    #如果WORD是>0     
                    else:
                    #轉成16進位
                        hex_WORD = hex(ten_WORD)[2:]
                        sumstr_word=""
                        #如果字串長度不等於6 要補0
                        if(len(hex_WORD)!=6):
                            for i in range(6-len(hex_WORD)):
                                sumstr_word+="0"
                        row.append((sumstr_word+hex_WORD).upper())     
       
#印出來
def print_re_arr(re_arr=[[]]):
    for index_row,row in enumerate(re_arr):
        for index_col,col in enumerate(row):     
            if(index_col==len(re_arr[index_row])-1):   
                print('%-13s' % re_arr[index_row][index_col])
            else:
                print('%-13s' % re_arr[index_row][index_col],end="")
        
"""主程式"""
Loc = 0 
            
symbol={}                
arr = []
one_d_arr=[]
re_arr = []
data_name = "SIC_XE.txt"
read_file(data_name,arr)
reshape_arr(one_d_arr,re_arr,arr)

loc_count(Loc,re_arr)
symbol_lookup(re_arr)

operand_def(re_arr)

print_re_arr(re_arr)