"""
Security vulnerability scanner.
Detects common security issues in source code.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


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
    """Multi-language security vulnerability scanner"""

    SQL_INJECTION_PATTERNS = [
        (
            r'(execute|cursor\.execute|executemany)\s*\(\s*["\'].*%s.*["\']',
            "Python SQL string formatting",
        ),
        (
            r"(execute|cursor\.execute|executemany)\s*\(\s*.*\+\s*",
            "Python SQL string concatenation",
        ),
        (r'(execute|cursor\.execute|executemany)\s*\(\s*f["\']', "Python SQL f-string"),
        (r"sprintf\s*\(.*SELECT|INSERT|UPDATE|DELETE", "C SQL injection via sprintf"),
        (r"strcat\s*\(.*SELECT|INSERT|UPDATE|DELETE", "C SQL injection via strcat"),
        (r"EXEC\s+SQL.*:(\w+)", "COBOL dynamic SQL variable"),
    ]

    SECRET_PATTERNS = [
        (r'["\']([A-Za-z0-9_-]{32,})["\']', "API Key"),
        (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', "API Key assignment"),
        (r'password\s*=\s*["\']([^"\']+)["\']', "Hardcoded password"),
        (r'passwd\s*=\s*["\']([^"\']+)["\']', "Hardcoded password"),
        (r'pwd\s*=\s*["\']([^"\']+)["\']', "Hardcoded password"),
        (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
        (r'aws_secret_access_key\s*=\s*["\']([^"\']+)["\']', "AWS Secret Key"),
        (
            r"(postgresql|mysql|mongodb)://[^:]+:([^@]+)@",
            "Database password in connection string",
        ),
        (r"-----BEGIN (RSA |DSA )?PRIVATE KEY-----", "Private key"),
        (r'token\s*=\s*["\']([A-Za-z0-9_-]{20,})["\']', "Hardcoded token"),
        (r"bearer\s+[A-Za-z0-9_-]{20,}", "Bearer token"),
    ]

    COMMAND_INJECTION_PATTERNS = [
        (r"os\.system\s*\(.*\+", "os.system with string concatenation"),
        (r'os\.system\s*\(\s*f["\']', "os.system with f-string"),
        (
            r"subprocess\.(call|run|Popen)\s*\(.*shell\s*=\s*True",
            "subprocess with shell=True",
        ),
        (r"exec\s*\(", "exec() with dynamic code"),
        (r"eval\s*\(", "eval() with dynamic code"),
        (r"system\s*\(", "C system() call"),
        (r"popen\s*\(", "C popen() call"),
        (r"execve?\s*\(", "C exec family call"),
    ]

    PATH_TRAVERSAL_PATTERNS = [
        (r"\.\./", "Path traversal attempt (../)"),
        (r"\.\.[/\\]", "Path traversal attempt (../)"),
        (r"open\s*\(.*\+", "File open with concatenation (potential path traversal)"),
        (r"(fopen|open|read)\s*\([^)]*%s", "File operation with format string"),
    ]

    XSS_PATTERNS = [
        (r"<.*\{.*\}.*>", "Template injection risk"),
        (r"innerHTML\s*=", "Direct innerHTML assignment"),
        (r"document\.write\s*\(", "document.write (XSS risk)"),
        (r"eval\s*\(.*request\.", "eval with user input"),
        (r"\.html\s*\(.*\+", "jQuery .html() with concatenation"),
        (r"dangerouslySetInnerHTML", "React dangerouslySetInnerHTML"),
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
            "recommendation": "Avoid shell=True. Use subprocess with argument lists. Validate and sanitize all user input.",
        },
        "Path Traversal": {
            "cwe": "CWE-22",
            "owasp": "A01:2021 - Broken Access Control",
            "recommendation": "Validate file paths. Use os.path.abspath() and check if path starts with allowed directory.",
        },
        "XSS": {
            "cwe": "CWE-79",
            "owasp": "A03:2021 - Injection",
            "recommendation": "Always escape user input before rendering in HTML. Use templating engines with auto-escaping.",
        },
    }

    def scan_file(
        self, file_path: str, content: str, language: str
    ) -> List[SecurityIssue]:
        """
        Scan a file for security vulnerabilities.

        Args:
            file_path: Path to the file
            content: File content
            language: Programming language

        Returns:
            List of security issues found
        """
        issues = []
        lines = content.split("\n")
        issues.extend(self._check_sql_injection(lines, file_path))
        issues.extend(self._check_hardcoded_secrets(lines, file_path))
        issues.extend(self._check_command_injection(lines, file_path))
        issues.extend(self._check_path_traversal(lines, file_path))
        if language in ["python", "javascript", "typescript"]:
            issues.extend(self._check_xss(lines, file_path))
        return issues

    def _check_sql_injection(
        self, lines: List[str], file_path: str
    ) -> List[SecurityIssue]:
        """Detect SQL injection vulnerabilities"""
        issues = []
        for line_num, line in enumerate(lines, start=1):
            for pattern, description in self.SQL_INJECTION_PATTERNS:
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
        self, lines: List[str], file_path: str
    ) -> List[SecurityIssue]:
        """Detect hardcoded secrets (passwords, API keys, tokens)"""
        issues = []
        for line_num, line in enumerate(lines, start=1):
            if line.strip().startswith("#") or line.strip().startswith("//"):
                continue
            for pattern, secret_type in self.SECRET_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    if any(
                        fp in line.lower()
                        for fp in ["example", "test", "dummy", "placeholder", "xxx"]
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
        self, lines: List[str], file_path: str
    ) -> List[SecurityIssue]:
        """Detect command injection vulnerabilities"""
        issues = []
        for line_num, line in enumerate(lines, start=1):
            for pattern, description in self.COMMAND_INJECTION_PATTERNS:
                if re.search(pattern, line):
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
                            confidence="high",
                        )
                    )
        return issues

    def _check_path_traversal(
        self, lines: List[str], file_path: str
    ) -> List[SecurityIssue]:
        """Detect path traversal vulnerabilities"""
        issues = []
        for line_num, line in enumerate(lines, start=1):
            for pattern, description in self.PATH_TRAVERSAL_PATTERNS:
                if re.search(pattern, line):
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

    def _check_xss(self, lines: List[str], file_path: str) -> List[SecurityIssue]:
        """Detect XSS vulnerabilities"""
        issues = []
        for line_num, line in enumerate(lines, start=1):
            for pattern, description in self.XSS_PATTERNS:
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

    @staticmethod
    def _redact_secret(text: str) -> str:
        """Redact secrets in code snippets for safe display"""
        return re.sub(r'["\']([A-Za-z0-9_-]{8,})["\']', r'"***REDACTED***"', text)
