#include <stdlib.h>
#include <string.h>

#define MAX_ALLOCATIONS 100

typedef struct {
    void* ptr;
    size_t size;
    int in_use;
} MemoryBlock;

static MemoryBlock memory_pool[MAX_ALLOCATIONS];

/**
 * Custom memory allocation with tracking
 */
void* memory_allocate(size_t size) {
    void* ptr = malloc(size);
    if (ptr == NULL) {
        return NULL;
    }
    
    // Track allocation
    for (int i = 0; i < MAX_ALLOCATIONS; i++) {
        if (!memory_pool[i].in_use) {
            memory_pool[i].ptr = ptr;
            memory_pool[i].size = size;
            memory_pool[i].in_use = 1;
            break;
        }
    }
    
    return ptr;
}

/**
 * Free tracked memory
 */
void memory_free(void* ptr) {
    for (int i = 0; i < MAX_ALLOCATIONS; i++) {
        if (memory_pool[i].ptr == ptr && memory_pool[i].in_use) {
            free(ptr);
            memory_pool[i].in_use = 0;
            break;
        }
    }
}

/**
 * Get total allocated memory
 */
size_t get_total_allocated() {
    size_t total = 0;
    for (int i = 0; i < MAX_ALLOCATIONS; i++) {
        if (memory_pool[i].in_use) {
            total += memory_pool[i].size;
        }
    }
    return total;
}

