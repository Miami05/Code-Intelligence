; string_operations.asm - String manipulation functions
; Platform: x86-64

section .data
    buffer times 256 db 0

section .text
    global string_length
    global string_copy
    global string_compare
    global string_to_upper

; Calculate string length
; Parameters: rdi = pointer to string
; Returns: rax = length
string_length:
    xor rax, rax
.loop:
    cmp byte [rdi + rax], 0
    je .done
    inc rax
    jmp .loop
.done:
    ret

; Copy string from source to destination
; Parameters: rdi = destination, rsi = source
; Returns: rax = destination pointer
string_copy:
    push rdi
.loop:
    mov al, [rsi]
    mov [rdi], al
    test al, al
    jz .done
    inc rsi
    inc rdi
    jmp .loop
.done:
    pop rax
    ret

; Compare two strings
; Parameters: rdi = string1, rsi = string2
; Returns: rax = 0 if equal, -1 if str1 < str2, 1 if str1 > str2
string_compare:
.loop:
    mov al, [rdi]
    mov bl, [rsi]
    cmp al, bl
    jl .less
    jg .greater
    test al, al
    jz .equal
    inc rdi
    inc rsi
    jmp .loop

.equal:
    xor rax, rax
    ret
.less:
    mov rax, -1
    ret
.greater:
    mov rax, 1
    ret

; Convert string to uppercase
; Parameters: rdi = pointer to string
; Returns: rax = pointer to string
string_to_upper:
    push rdi
.loop:
    mov al, [rdi]
    test al, al
    jz .done
    
    cmp al, 'a'
    jl .next
    cmp al, 'z'
    jg .next
    
    sub al, 32
    mov [rdi], al
    
.next:
    inc rdi
    jmp .loop
.done:
    pop rax
    ret

