; memory_utils.asm - Memory management utilities
; Platform: x86-64

section .text
    global memory_set
    global memory_copy
    global memory_compare

; Set memory to a specific value
; Parameters: rdi = destination, rsi = value, rdx = count
; Returns: rax = destination pointer
memory_set:
    push rdi
    mov rcx, rdx
    mov al, sil
    rep stosb
    pop rax
    ret

; Copy memory from source to destination
; Parameters: rdi = destination, rsi = source, rdx = count
; Returns: rax = destination pointer
memory_copy:
    push rdi
    mov rcx, rdx
    rep movsb
    pop rax
    ret

; Compare two memory regions
; Parameters: rdi = memory1, rsi = memory2, rdx = count
; Returns: rax = 0 if equal, non-zero otherwise
memory_compare:
    mov rcx, rdx
    repe cmpsb
    jne .not_equal
    xor rax, rax
    ret
.not_equal:
    mov rax, 1
    ret

; Allocate memory on stack
; Parameters: rdi = size in bytes
; Returns: rax = pointer to allocated memory
stack_allocate:
    sub rsp, rdi
    mov rax, rsp
    ret

; Free stack memory
; Parameters: rdi = size in bytes
stack_free:
    add rsp, rdi
    ret

