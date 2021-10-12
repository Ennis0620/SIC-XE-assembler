SIC-XE-assembler
===
# Introduction
相較於SIC需要更多的步驟，SIC/XE有4種指令格式，是SIC的進階版

# Detail
SIC/XE有4種指令格式


| 指令格式 |  | | |
| ---|---|---|---|
| Type1 | Opcode:8 | | |
| Type2 | Opcode:8 |R1:4 |R2:4 |
| Type3 | Opcode:8 |n	i	x	b	p	e |disp:12 |
| Type4  |Opcode:8 |n	i	x	b	p	e |address:20 |

暫存器:比SIC多了 B(基底)、S、T(一般用途)、F(浮點累加)

### 讀檔:存取Symbol、Instruction、Operand，不存註解行
### 處理格式
### 處理Loc
1.BASE為宣告可以使用基底定址，因此該行沒有Loc


2.其餘跟SIC處理的方式相同，但是要注意的是有些指令有4種，因此需要對照其格式去增加Loc。

### 處理Object code:
1.解析是屬於何種格式

![](https://i.imgur.com/X1sMm9E.png)

</br>

m:代表文字

c:代表0~4095的10進位  若超過該範圍就是m

</br>

2.指令格式3,4的部分因為opcode長度關係必須和n,i共用

    ex. 001D STA BUFFER =>屬於op m  , disp = TA-(PC) = 36-(1D+3)=16


| OC(16進位)| |  | | | | |  | | | | | |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| |  | | | | | | n |i |x |b |p |e |
| |  | | | | | | 1 | 1| 0|0 | 1| 0|
|Opcode | 0| 0 | 0|0 | 0|0 |1  |1 | | | | |
| | | | | | | |n |i |x |b |p | e|
|計算結果| 0| 0 |0 |0 |1|1 |1  |1 |0 |0 |1 |0 |

| Object Code|  | | | | | |
|---|---|---|---|---|---|---|
| |0 |F  |2 |0 |1 |6 |



</br>

3.大部分指令定址大多都是PC相對定址disp=TA-PC，但是有些指令必須用BASE相對定址disp=TA-B
    
    ex.
    1056 STX LENGTH => op m ,disp = TA-(PC)=33-1059 =>超過12bits 塞不下
	   =>改採用disp=TA-(B) = 33-33=0
    
| Object Code(記得disp=12bits 要補滿位數)|  | | | | | |
|---|---|---|---|---|---|---|
| |1 |3  |4 |0 |0 |0 |

</br>

4.注意CLEAR X 若出現在 operand = ...,X 之前代表X已被清除，不用加8000

# Demo
執行結果
![](https://i.imgur.com/aGWFL0J.png)
![](https://i.imgur.com/C5Gi0M4.png)


# Requirement
    None
# Package
    SIC_XE
        SICXE_test.txt    更改數值輸入         
        SIC_XE.txt        輸入
        SIC_XE.py         主程式
# Problems

# Solve
