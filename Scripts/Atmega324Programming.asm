

; Replace with your application code
.NOLIST
.INCLUDE "m324adef.inc" ; 
.LIST

.DEF ValorADC = R20;		; define registo 20 para guardar o Valor do ADC
.DEF CanalADC = R21;		; define registo 21 para guardar o canal a ser amostrado

.CSEG
.ORG 0x0000
	JMP	INICIO				; salta os vetores de interrupcao para o INICIO

.CSEG
.ORG 0x0030					; quando se da interrupçao de conversao completa do ADC 
	JMP INT_HANDLER_ADC			; salta para Handler da interrupcao
	 

.CSEG
.ORG 0X0060					; inicia o codigo acima dos vetores de interrupcao
		
		
INICIO:
	;Timer:					; configuracao do timer
	LDS R16,TCCR0B				; copia valores do TCCR0B para R16
	LDI R17,0x02				; 0000 0010 para R17 ->(CS0 010: clock com prescaling de 8)
	OR  R16,R17     			; junta valores de R16 e R17 para R16(junta apenas alteraçoes)
	STS TCCR0B,R16  			; altera TCCR0B com as configuracoes em R16
	
	
	;ADC:					; configuracao do ADC
	LDS R16,ADCSRA				; copia valores do ADCSRA para R16
	LDI R17,0xA8			 	; 1010 1000 para R17 -> (ADEN 1: ativa adc / ADATE 1: ativa autotrigger / ADIE 1: ativa interrupcao de fim de conversao)
	OR  R16,R17					; junta valores de R16 e R17 para R16(junta apenas alteraçoes)
	STS ADCSRA,R16				; altera ADCSRA com as configuracoes em R16

	LDS R16,ADCSRB				; copia valores do ADCSRB para R16
	LDI R17,0x04				; 0000 0100 para R17 -> (ADTS 100: ativa autotrigger com overflow do clk0)
	OR  R16,R17					; junta valores de R16 e R17 para R16(junta apenas alteraçoes)
	STS ADCSRB,R16				; altera ADCSRB com as configuracoes em R16

	LDS R16,ADMUX   			; copia valores do ADMUX para R16
	LDI R17,0x60				; 0110 0000 para R17 -> (REFD 01: seleciona ref de 5V / ADLAR 1: left adjusted / MUX 00000: seleciona ADC0)
	OR  R16,R17					; junta valores de R16 e R17 para R16(junta apenas alteraçoes)
	STS ADMUX,R16				; altera ADMUX com as configuracoes em R16

	
	;USART:					; configuracao da USART
	LDI R17,0X00				
	LDI R16,0x0C				; 0000 0000 1100 para R17 e R16 -> (seleciona Baud de 4800 para freq osc de 1MHz)
	STS UBRR0H, r17				; altera UBRR0H com as configuracoes em R17
	STS UBRR0L, r16				; altera UBRR0L com as configuracoes em R16

	LDS R16,UCSR0B				; copia valores do UCSR0B para R16
	LDI r17,0x18   				; 0001 1000 para R17 -> (RXEN0 1: tansmiter enable / TXEN0 1: receiver enable)
	OR  R16,R17					; junta valores de R16 e R17 para R16(junta apenas alteraçoes)
	STS UCSR0B,r16				; altera UCSR0B com as configuracoes em R16

	LDS R16,UCSR0C				; copia valores do UCSR0C para R16
	LDI r17, 0x06   			; 0000 0110 para R17 -> (UPMO 00: sem bit paridade / USBS0 0: 1 stopbit / UCSZ0 011: 8 bit char size)
	OR  R16,R17					; junta valores de R16 e R17 para R16(junta apenas alteraçoes)
	STS UCSR0C,r16				; altera UCSR0C com as configuracoes em R16
	
	SEI							; ativa as interrupcoes globalmente
	

	
CICLO:						; ciclo main
	nop							; nao faz nada(incrementa clock)
	jmp CICLO					; repete ciclo

	
	
	
INT_HANDLER_ADC:				; Lida com a interrupcao de fim de conversao do ADC
	
	;limpa flags do timer0:
	LDI R16,111					; 0000 0111 para R16 -> para limpar as flags de interrupcao do timer
	OUT TIFR0,R16				; altera TIFR0 com as configuracoes em R16

	;le canal:
	LDS CanalADC, ADMUX   		; copia valores do ADMUX para registo de CanalADC
	LDI R17,0X01				; R17 = 0000 0001
	AND CanalADC,R17			; coloca todos os valores a 0, menos o ultimo(contem o canal ADC do ADMUX) e coloca no registo CanalADC

	;le valor:
	LDS ValorADC,ADCH			; Le 8 bits mais significativos do ADC e coloca no registo ValorADC

	;comuta o canal do ADC:
	LDS R16,ADMUX				; copia valores do ADMUX para R16
	LDI R17,0x01				; R17 = 0000 0001
	EOR R16,R17					; mantem todos valores menos o ultimo, que irá comutar, alterando o canal do ADC
	STS ADMUX,R16				; altera ADMUX com as configuracoes em R16

	;envio porta serie:
	LDI R17,0XFE     			; R17 = 1111 1110
	AND ValorADC,R17 			; ValorADC = ValorADC com o ultimo bit a 0
	OR  ValorADC,CanalADC 		; coloca CanalADC no ultimo bit

	STS UDR0,ValorADC			; coloca caracter no buffer da porta serie para ser enviado

	RETI						; retorna da interrupcao para a posicao anterior
