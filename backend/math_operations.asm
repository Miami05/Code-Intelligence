; math_operations.asm - Basic arithmetic operations
; Platform: x86-64

section .data
    num1 dq 10
    num2 dq 20
    result dq 0
    msg db "Result: ", 0

section .text
    global _start
    global add_numbers
    global subtract_numbers
    global multiply_numbers

; Add two numbers
; Parameters: rdi = first number, rsi = second number
; Returns: rax = sum
add_numbers:
    mov rax, rdi
    add rax, rsi
    ret

; Subtract two numbers
; Parameters: rdi = first number, rsi = second number
; Returns: rax = difference
subtract_numbers:
    mov rax, rdi
    sub rax, rsi
    ret

; Multiply two numbers
; Parameters: rdi = first number, rsi = second number
; Returns: rax = product
multiply_numbers:
    mov rax, rdi
    imul rax, rsi
    ret

; Calculate factorial
; Parameters: rdi = number
; Returns: rax = factorial
calculate_factorial:
    cmp rdi, 1
    jle .base_case
    
    push rdi
    dec rdi
    call calculate_factorial
    pop rdi
    imul rax, rdi
    ret

.base_case:
    mov rax, 1
    ret

_start:
    ; Add numbers
    mov rdi, [num1]
    mov rsi, [num2]
    call add_numbers
    mov [result], rax
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall

