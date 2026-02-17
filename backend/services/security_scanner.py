"""
Security vulnerability scanner.
Detects common security issues in source code.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


@dataclass
class SecurityIssue:
    """Represents a detected security vulnerability"""

    type: str
    severity: str
    line_number: int
    code_snippet: str
    description: str
    recommendation: str
    cwe_id: str
    owasp_category: str
    confidence: str


class SecurityScanner:
    """Multi-language security vulnerability scanner with language awareness"""

    SQL_INJECTION_PATTERNS = [
        # Python-specific patterns (unsafe)
        (
            r'(execute|cursor\.execute|executemany)\s*\(\s*["\'].*%s.*["\']',
            "Python SQL string formatting",
            ["python"],
        ),
        (
            r"(execute|cursor\.execute|executemany)\s*\(\s*.*\+\s*",
            "Python SQL string concatenation",
            ["python"],
        ),
        (
            r'(execute|cursor\.execute|executemany)\s*\(\s*f["\']',
            "Python SQL f-string",
            ["python"],
        ),
        (
            r"sprintf\s*\([^)]*\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\b",
            "C SQL injection via sprintf",
            ["c", "cpp"],
        ),
        (
            r"strcat\s*\([^)]*\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\b",
            "C SQL injection via strcat",
            ["c", "cpp"],
        ),
        (r"EXEC\s+SQL.*:(\w+)", "COBOL dynamic SQL variable", ["cobol"]),
        (
            r"STRING\s+.*\bSELECT\b.*INTO",
            "COBOL SQL string concatenation",
            ["cobol"],
        ),
        (
            r"EXEC\s+SQL\s+PREPARE.*FROM\s+:(\w+)",
            "COBOL prepared statement with variable",
            ["cobol"],
        ),
    ]

    SECRET_PATTERNS = [
        (r'["\']([A-Za-z0-9_-]{40,})["\']', "API Key", []),
        (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', "API Key assignment", []),
        (r'password\s*=\s*["\']([^"\']{8,})["\']', "Hardcoded password", []),
        (r'passwd\s*=\s*["\']([^"\']{8,})["\']', "Hardcoded password", []),
        (r'pwd\s*=\s*["\']([^"\']{8,})["\']', "Hardcoded password", []),
        (r"AKIA[0-9A-Z]{16}", "AWS Access Key", []),
        (r'aws_secret_access_key\s*=\s*["\']([^"\']+)["\']', "AWS Secret Key", []),
        (
            r"(postgresql|mysql|mongodb)://[^:]+:([^@]+)@",
            "Database password in connection string",
            [],
        ),
        (r"-----BEGIN (RSA |DSA )?PRIVATE KEY-----", "Private key", []),
        (r'token\s*=\s*["\']([A-Za-z0-9_-]{30,})["\']', "Hardcoded token", []),
        (r"bearer\s+[A-Za-z0-9_-]{30,}", "Bearer token", []),
        (
            r"(PASSWORD|PASSWD|PWD)\s+PIC\s+X.*VALUE\s+['\"]([^'\"]{8,})",
            "COBOL hardcoded password",
            ["cobol"],
        ),
        (
            r"(API-KEY|APIKEY|TOKEN)\s+PIC\s+X.*VALUE\s+['\"]([^'\"]{20,})",
            "COBOL hardcoded API key",
            ["cobol"],
        ),
        (
            r"(password|passwd|pwd).*db\s+['\"]([^'\"]{8,})",
            "Assembly hardcoded password in .data",
            ["assembly"],
        ),
        (
            r"(api_key|apikey|token).*db\s+['\"]([^'\"]{20,})",
            "Assembly hardcoded API key",
            ["assembly"],
        ),
    ]

    COMMAND_INJECTION_PATTERNS = [
        (
            r"os\.system\s*\(.*\+",
            "os.system with string concatenation",
            ["python"],
        ),
        (r'os\.system\s*\(\s*f["\']', "os.system with f-string", ["python"]),
        (
            r"subprocess\.(call|run|Popen)\s*\(.*shell\s*=\s*True",
            "subprocess with shell=True",
            ["python"],
        ),
        (r"exec\s*\(", "exec() with dynamic code", ["python"]),
        (r"eval\s*\(", "eval() with dynamic code", ["python", "javascript"]),
        (r"system\s*\(", "C system() call", ["c", "cpp"]),
        (r"popen\s*\(", "C popen() call", ["c", "cpp"]),
        (
            r"execve?\s*\([^)]*argv",
            "execve() with potentially unsafe input",
            ["c", "cpp"],
        ),
        (
            r"CALL\s+['\"]SYSTEM['\"]\s+USING",
            "COBOL CALL SYSTEM with parameter",
            ["cobol"],
        ),
        (
            r"CALL\s+['\"]CBL_EXEC_RUN_CMD['\"].*USING",
            "COBOL execute command with parameter",
            ["cobol"],
        ),
        (
            r"int\s+0x80.*eax.*0xb",
            "Assembly execve syscall (potential command injection)",
            ["assembly"],
        ),
        (
            r"syscall.*__NR_execve",
            "Assembly execve syscall (potential command injection)",
            ["assembly"],
        ),
    ]

    PATH_TRAVERSAL_PATTERNS = [
        (
            r"(fopen|open|fread|fwrite|remove|unlink)\s*\([^)]*\.\.",
            "File operation with path traversal (../)",
            ["c", "cpp"],
        ),
        (
            r"open\s*\(.*\+",
            "File open with concatenation (potential path traversal)",
            ["python"],
        ),
        (
            r"(OPEN|READ|WRITE)\s+(INPUT|OUTPUT)\s+\w+.*\.\.",
            "COBOL file operation with path traversal (../)",
            ["cobol"],
        ),
        (
            r"SELECT\s+\w+\s+ASSIGN.*STRING\s+.*\+",
            "COBOL dynamic file path (potential traversal)",
            ["cobol"],
        ),
        (
            r"int\s+0x80.*eax.*(0x5|0x3|0x4).*ebx.*\.\.",
            "Assembly file syscall with path traversal",
            ["assembly"],
        ),
    ]

    BUFFER_OVERFLOW_PATTERNS = [
        (r"gets\s*\(", "Unsafe gets() - buffer overflow risk", ["c", "cpp"]),
        (r"strcpy\s*\(", "Unsafe strcpy() - no bounds checking", ["c", "cpp"]),
        (r"strcat\s*\(", "Unsafe strcat() - no bounds checking", ["c", "cpp"]),
        (r"sprintf\s*\(", "Unsafe sprintf() - use snprintf instead", ["c", "cpp"]),
        (
            r"scanf\s*\([^)]*%s",
            "Unsafe scanf with %s - buffer overflow risk",
            ["c", "cpp"],
        ),
        (
            r"rep\s+movs[bwd]",
            "Assembly unchecked memory copy (rep movs)",
            ["assembly"],
        ),
        (
            r"(push|pop)\s+.*esp.*add.*esp",
            "Assembly manual stack manipulation (potential overflow)",
            ["assembly"],
        ),
        (
            r"STRING\s+.*DELIMITED.*INTO\s+\w+\s+ON\s+OVERFLOW",
            "COBOL STRING operation without overflow handling",
            ["cobol"],
        ),
    ]

    XSS_PATTERNS = [
        (
            r"(render_template|render_to_string)\s*\(.*\{.*\}",
            "Template rendering with unsafe variables",
            ["python"],
        ),
        (r"innerHTML\s*=", "Direct innerHTML assignment", ["javascript", "typescript"]),
        (
            r"document\.write\s*\(",
            "document.write (XSS risk)",
            ["javascript", "typescript"],
        ),
        (
            r"eval\s*\(.*request\.",
            "eval with user input",
            ["javascript", "typescript"],
        ),
        (
            r"\.html\s*\(.*\+",
            "jQuery .html() with concatenation",
            ["javascript", "typescript"],
        ),
        (
            r"dangerouslySetInnerHTML",
            "React dangerouslySetInnerHTML",
            ["javascript", "typescript"],
        ),
    ]

    SQLALCHEMY_SAFE_PATTERNS = [
        r"\.query\(",  # db.query(Model)
        r"\.filter\(",  # .filter(Model.id == ...)
        r"\.filter_by\(",  # .filter_by(id=...)
        r"mapped_column\(",  # SQLAlchemy 2.0 column definitions
        r"relationship\(",  # relationship definitions
        r"Mapped\[",  # Type annotations
        r"__repr__",  # Python debug representations
        r"__str__",  # Python string representations
        r"f[\"']<.*>.*[\"']",  # f-strings that just format debug output
    ]

    C_PREPROCESSOR_PATTERNS = [
        r"^\s*#\s*include",  # #include statements
        r"^\s*#\s*define",  # #define macros
        r"^\s*#\s*if",  # #if, #ifdef, #ifndef
        r"^\s*#\s*endif",  # #endif
        r"^\s*#\s*pragma",  # #pragma directives
        r"^\s*#\s*undef",  # #undef
    ]

    ASSEMBLY_DIRECTIVES = [
        r"^\s*%include",  # NASM %include
        r"^\s*\.include",  # GAS .include
        r"^\s*INCLUDE",  # MASM INCLUDE
        r"^\s*\.data",  # Data section
        r"^\s*\.text",  # Code section
        r"^\s*\.bss",  # BSS section
        r"^\s*;.*",  # Comments
    ]

    COBOL_COMMENTS = [
        r"^\s*\*",  # COBOL comment line (starts with *)
        r"^......\*",  # COBOL comment (column 7 is *)
    ]

    VULNERABILITY_METADATA = {
        "SQL Injection": {
            "cwe": "CWE-89",
            "owasp": "A03:2021 - Injection",
            "recommendation": "Use parameterized queries or prepared statements. Never concatenate user input into SQL strings.",
        },
        "Hardcoded Secret": {
            "cwe": "CWE-798",
            "owasp": "A07:2021 - Identification and Authentication Failures",
            "recommendation": "Store secrets in environment variables or secure vaults (e.g., AWS Secrets Manager, HashiCorp Vault).",
        },
        "Command Injection": {
            "cwe": "CWE-78",
            "owasp": "A03:2021 - Injection",
            "recommendation": "Avoid shell=True. Use subprocess with argument lists. Validate and sanitize all user input. For execve(), ensure arguments are properly validated.",
        },
        "Path Traversal": {
            "cwe": "CWE-22",
            "owasp": "A01:2021 - Broken Access Control",
            "recommendation": "Validate file paths. Use os.path.abspath() and check if path starts with allowed directory. In C, use realpath() and validate paths.",
        },
        "XSS": {
            "cwe": "CWE-79",
            "owasp": "A03:2021 - Injection",
            "recommendation": "Always escape user input before rendering in HTML. Use templating engines with auto-escaping.",
        },
        "Buffer Overflow": {
            "cwe": "CWE-120",
            "owasp": "A03:2021 - Injection",
            "recommendation": "Use safe string functions (strncpy, snprintf, fgets). Always check buffer bounds. In Assembly, validate all memory operations.",
        },
    }

    def scan_file(
        self, file_path: str, content: str, language: str
    ) -> List[SecurityIssue]:
        """
        Scan a file for security vulnerabilities with language awareness.

        Args:
            file_path: Path to the file
            content: File content
            language: Programming language (lowercased)

        Returns:
            List of unique security issues found
        """
        issues = []
        lines = content.split("\n")
        language_lower = language.lower() if language else ""

        issues.extend(self._check_sql_injection(lines, file_path, language_lower))
        issues.extend(self._check_hardcoded_secrets(lines, file_path, language_lower))
        issues.extend(self._check_command_injection(lines, file_path, language_lower))
        issues.extend(self._check_path_traversal(lines, file_path, language_lower))
        issues.extend(self._check_buffer_overflow(lines, file_path, language_lower))

        if language_lower in ["python", "javascript", "typescript"]:
            issues.extend(self._check_xss(lines, file_path, language_lower))

        return self._deduplicate_issues(issues)

    def _is_c_preprocessor_directive(self, line: str) -> bool:
        """
        Check if line is a C/C++ preprocessor directive.
        These are not security vulnerabilities - they're compiler directives.
        """
        return any(re.match(pattern, line) for pattern in self.C_PREPROCESSOR_PATTERNS)

    def _is_assembly_directive(self, line: str) -> bool:
        """Check if line is an Assembly directive or comment (not code)."""
        return any(re.match(pattern, line) for pattern in self.ASSEMBLY_DIRECTIVES)

    def _is_cobol_comment(self, line: str) -> bool:
        """Check if line is a COBOL comment."""
        return any(re.match(pattern, line) for pattern in self.COBOL_COMMENTS)

    def _is_sqlalchemy_safe(self, line: str) -> bool:
        """Check if line is safe SQLAlchemy ORM usage or Python debug output"""
        return any(
            re.search(pattern, line) for pattern in self.SQLALCHEMY_SAFE_PATTERNS
        )

    def _should_check_pattern(
        self, pattern_languages: List[str], current_language: str
    ) -> bool:
        """
        Check if a pattern should be applied to the current language.

        Args:
            pattern_languages: List of languages this pattern applies to (empty = all)
            current_language: Current file's language

        Returns:
            True if pattern should be checked
        """
        if not pattern_languages:
            return True
        return current_language in pattern_languages

    def _check_sql_injection(
        self, lines: List[str], file_path: str, language: str
    ) -> List[SecurityIssue]:
        """Detect SQL injection vulnerabilities with language context"""
        issues = []
        for line_num, line in enumerate(lines, start=1):
            if language in ["c", "cpp"] and self._is_c_preprocessor_directive(line):
                continue
            if language == "assembly" and self._is_assembly_directive(line):
                continue
            if language == "cobol" and self._is_cobol_comment(line):
                continue

            if self._is_sqlalchemy_safe(line):
                continue

            for pattern, description, languages in self.SQL_INJECTION_PATTERNS:
                if not self._should_check_pattern(languages, language):
                    continue

                if re.search(pattern, line, re.IGNORECASE):
                    metadata = self.VULNERABILITY_METADATA["SQL Injection"]
                    issues.append(
                        SecurityIssue(
                            type="SQL Injection",
                            severity="critical",
                            line_number=line_num,
                            code_snippet=line.strip(),
                            description=f"Potential SQL injection: {description}",
                            recommendation=metadata["recommendation"],
                            cwe_id=metadata["cwe"],
                            owasp_category=metadata["owasp"],
                            confidence="high",
                        )
                    )
        return issues

    def _check_hardcoded_secrets(
        self, lines: List[str], file_path: str, language: str
    ) -> List[SecurityIssue]:
        """Detect hardcoded secrets (passwords, API keys, tokens)"""
        issues = []
        for line_num, line in enumerate(lines, start=1):
            # Skip comments and directives
            if line.strip().startswith(("#", "//", "/*", "*")):
                continue

            if language in ["c", "cpp"] and self._is_c_preprocessor_directive(line):
                continue
            if language == "assembly" and self._is_assembly_directive(line):
                continue
            if language == "cobol" and self._is_cobol_comment(line):
                continue

            for pattern, secret_type, languages in self.SECRET_PATTERNS:
                if not self._should_check_pattern(languages, language):
                    continue

                if re.search(pattern, line, re.IGNORECASE):
                    # More comprehensive false positive filtering
                    if any(
                        fp in line.lower()
                        for fp in [
                            "example",
                            "test",
                            "dummy",
                            "placeholder",
                            "xxx",
                            "sample",
                            "default",
                            "todo",
                            "fixme",
                            "your_",
                            "<your",
                            "SECRET_KEY",  # Django setting name
                            "os.environ",  # Environment variable reference
                            "getenv",
                        ]
                    ):
                        continue

                    metadata = self.VULNERABILITY_METADATA["Hardcoded Secret"]
                    issues.append(
                        SecurityIssue(
                            type="Hardcoded Secret",
                            severity="high",
                            line_number=line_num,
                            code_snippet=self._redact_secret(line.strip()),
                            description=f"Hardcoded {secret_type} detected",
                            recommendation=metadata["recommendation"],
                            cwe_id=metadata["cwe"],
                            owasp_category=metadata["owasp"],
                            confidence="medium",
                        )
                    )
        return issues

    def _check_command_injection(
        self, lines: List[str], file_path: str, language: str
    ) -> List[SecurityIssue]:
        """Detect command injection vulnerabilities"""
        issues = []
        for line_num, line in enumerate(lines, start=1):
            # Skip directives/comments
            if language in ["c", "cpp"] and self._is_c_preprocessor_directive(line):
                continue
            if language == "assembly" and self._is_assembly_directive(line):
                continue
            if language == "cobol" and self._is_cobol_comment(line):
                continue

            for pattern, description, languages in self.COMMAND_INJECTION_PATTERNS:
                if not self._should_check_pattern(languages, language):
                    continue

                if re.search(pattern, line, re.IGNORECASE):
                    metadata = self.VULNERABILITY_METADATA["Command Injection"]
                    issues.append(
                        SecurityIssue(
                            type="Command Injection",
                            severity="critical",
                            line_number=line_num,
                            code_snippet=line.strip(),
                            description=f"Potential command injection: {description}",
                            recommendation=metadata["recommendation"],
                            cwe_id=metadata["cwe"],
                            owasp_category=metadata["owasp"],
                            confidence="medium",
                        )
                    )
        return issues

    def _check_path_traversal(
        self, lines: List[str], file_path: str, language: str
    ) -> List[SecurityIssue]:
        """Detect path traversal vulnerabilities (excluding normal includes)"""
        issues = []
        for line_num, line in enumerate(lines, start=1):
            # Skip directives (includes are NORMAL)
            if language in ["c", "cpp"] and self._is_c_preprocessor_directive(line):
                continue
            if language == "assembly" and self._is_assembly_directive(line):
                continue
            if language == "cobol" and self._is_cobol_comment(line):
                continue

            for pattern, description, languages in self.PATH_TRAVERSAL_PATTERNS:
                if not self._should_check_pattern(languages, language):
                    continue

                if re.search(pattern, line, re.IGNORECASE):
                    metadata = self.VULNERABILITY_METADATA["Path Traversal"]
                    issues.append(
                        SecurityIssue(
                            type="Path Traversal",
                            severity="high",
                            line_number=line_num,
                            code_snippet=line.strip(),
                            description=description,
                            recommendation=metadata["recommendation"],
                            cwe_id=metadata["cwe"],
                            owasp_category=metadata["owasp"],
                            confidence="medium",
                        )
                    )
        return issues

    def _check_buffer_overflow(
        self, lines: List[str], file_path: str, language: str
    ) -> List[SecurityIssue]:
        """Detect buffer overflow vulnerabilities (C, Assembly, COBOL)"""
        issues = []
        # Only check languages where buffer overflow is relevant
        if language not in ["c", "cpp", "assembly", "cobol"]:
            return issues

        for line_num, line in enumerate(lines, start=1):
            # Skip directives/comments
            if language in ["c", "cpp"] and self._is_c_preprocessor_directive(line):
                continue
            if language == "assembly" and self._is_assembly_directive(line):
                continue
            if language == "cobol" and self._is_cobol_comment(line):
                continue

            for pattern, description, languages in self.BUFFER_OVERFLOW_PATTERNS:
                if not self._should_check_pattern(languages, language):
                    continue

                if re.search(pattern, line, re.IGNORECASE):
                    metadata = self.VULNERABILITY_METADATA["Buffer Overflow"]
                    issues.append(
                        SecurityIssue(
                            type="Buffer Overflow",
                            severity="critical",
                            line_number=line_num,
                            code_snippet=line.strip(),
                            description=description,
                            recommendation=metadata["recommendation"],
                            cwe_id=metadata["cwe"],
                            owasp_category=metadata["owasp"],
                            confidence="medium",
                        )
                    )
        return issues

    def _check_xss(
        self, lines: List[str], file_path: str, language: str
    ) -> List[SecurityIssue]:
        """Detect XSS vulnerabilities (only in actual HTML rendering contexts)"""
        issues = []
        for line_num, line in enumerate(lines, start=1):
            # Skip Python __repr__ and __str__ methods (they're debug output)
            if self._is_sqlalchemy_safe(line):
                continue

            for pattern, description, languages in self.XSS_PATTERNS:
                if not self._should_check_pattern(languages, language):
                    continue

                if re.search(pattern, line):
                    metadata = self.VULNERABILITY_METADATA["XSS"]
                    issues.append(
                        SecurityIssue(
                            type="XSS",
                            severity="high",
                            line_number=line_num,
                            code_snippet=line.strip(),
                            description=f"Potential XSS: {description}",
                            recommendation=metadata["recommendation"],
                            cwe_id=metadata["cwe"],
                            owasp_category=metadata["owasp"],
                            confidence="medium",
                        )
                    )
        return issues

    def _deduplicate_issues(self, issues: List[SecurityIssue]) -> List[SecurityIssue]:
        """
        Remove duplicate issues based on type, line number, and description.

        Args:
            issues: List of security issues

        Returns:
            Deduplicated list of issues
        """
        seen: Set[Tuple[str, int, str]] = set()
        unique_issues = []

        for issue in issues:
            # Create unique key from type, line number, and description
            key = (issue.type, issue.line_number, issue.description)
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)

        return unique_issues

    @staticmethod
    def _redact_secret(text: str) -> str:
        """Redact secrets in code snippets for safe display"""
        # Redact longer strings to avoid false positives on short variable names
        return re.sub(r'["\']([A-Za-z0-9_-]{12,})["\']', r'"***REDACTED***"', text)
