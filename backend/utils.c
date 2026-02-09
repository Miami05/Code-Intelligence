#include <stdio.h>
#include <string.h>
#include <ctype.h>

/**
 * Calculate the sum of an array
 */
int calculate_sum(int* numbers, int count) {
    int sum = 0;
    for (int i = 0; i < count; i++) {
        sum += numbers[i];
    }
    return sum;
}

/**
 * Calculate average of numbers
 */
double calculate_average(int* numbers, int count) {
    if (count == 0) return 0.0;
    return (double)calculate_sum(numbers, count) / count;
}

/**
 * Convert string to uppercase
 */
void string_to_upper(char* str) {
    for (int i = 0; str[i] != '\0'; i++) {
        str[i] = toupper((unsigned char)str[i]);
    }
}

/**
 * Validate email format
 */
int validate_email(const char* email) {
    if (email == NULL) return 0;
    
    const char* at = strchr(email, '@');
    const char* dot = strrchr(email, '.');
    
    return (at != NULL && dot != NULL && at < dot);
}

/**
 * Parse JSON-like string
 */
int parse_json_string(const char* json, char* key, char* value) {
    // Simplified JSON parsing
    sscanf(json, "{\"%[^\"]\":\"%[^\"]\"}", key, value);
    return 0;
}

