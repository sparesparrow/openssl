/**
 * @name OpenSSL Security Analysis Queries
 * @description Custom security queries for OpenSSL codebase
 * @kind problem
 * @id openssl/security/custom
 * @tags security
 * @precision high
 */

import cpp
import semmle.code.cpp.security.Security
import semmle.code.cpp.security.BufferWrite

/**
 * Improper EVP API usage patterns that could lead to security issues
 */
class ImproperEVPUse extends Expr {
  ImproperEVPUse() {
    // Detect missing error checking for EVP operations
    exists(FunctionCall call |
      call.getTarget().getName().matches("EVP_%") and
      not exists(IfStmt check | check.getCondition().getAChild*() = call) and
      not exists(Assignment assign | assign.getRValue() = call and
                  exists(IfStmt check | check.getCondition().getAChild*() = assign.getLValue()))
    )
  }
}

predicate isOpenSSLCryptoFunction(Function f) {
  f.getName().matches("EVP_%") or
  f.getName().matches("RSA_%") or
  f.getName().matches("ECDSA_%") or
  f.getName().matches("ECDH_%") or
  f.getName().matches("DH_%") or
  f.getName().matches("AES_%") or
  f.getName().matches("SHA%") or
  f.getName().matches("MD%") or
  f.getName().matches("HMAC_%") or
  f.getName().matches("CMAC_%") or
  f.getName().matches("RAND_%") or
  f.getName().matches("BN_%") or
  f.getName().matches("EC_%") or
  f.getName().matches("SSL_%") or
  f.getName().matches("BIO_%")
}

/**
 * Missing error handling in cryptographic operations
 */
from FunctionCall call, Function target
where
  isOpenSSLCryptoFunction(target) and
  call.getTarget() = target and
  // Check if there's no immediate error handling
  not exists(IfStmt check |
    check.getCondition().getAChild*() = call or
    exists(Variable v | v.getAnAssignedValue() = call and check.getCondition().getAChild*() = v)
  ) and
  // Not in test code
  not call.getFile().getBaseName().matches("%test%") and
  not call.getFile().getBaseName().matches("test_%")
select call, "Missing error handling for cryptographic operation: " + target.getName()

/**
 * Buffer overflow vulnerabilities in string operations
 */
from FunctionCall call
where
  call.getTarget().getName().matches("strcpy|strcat|sprintf|vsprintf|gets") and
  not call.getFile().getBaseName().matches("%test%")
select call, "Potentially unsafe string function usage: " + call.getTarget().getName()

/**
 * Timing attack vulnerabilities in cryptographic comparisons
 */
from FunctionCall call
where
  call.getTarget().getName().matches("memcmp|strcmp|strncmp") and
  call.getAnArgument().getType().toString().matches("%const unsigned char%") and
  exists(Function parent |
    parent = call.getEnclosingFunction() and
    isOpenSSLCryptoFunction(parent)
  ) and
  not call.getFile().getBaseName().matches("%test%")
select call, "Potential timing attack vulnerability in cryptographic comparison"

/**
 * Memory leaks in cryptographic operations
 */
from FunctionCall call, Function target
where
  isOpenSSLCryptoFunction(target) and
  call.getTarget() = target and
  // Functions that return allocated memory
  (target.getName().matches("EVP_MD_CTX_new|SSL_CTX_new|BIO_new|RAND_bytes%") or
   target.getName().matches("%_new")) and
  // Check if there's no corresponding free
  not exists(FunctionCall freeCall |
    freeCall.getTarget().getName().matches("%_free") and
    exists(Variable v |
      (v.getAnAssignedValue() = call or exists(Expr e | e = call and v.getAnAssignedValue() = e)) and
      freeCall.getAnArgument() = v
    )
  ) and
  not call.getFile().getBaseName().matches("%test%")
select call, "Potential memory leak in cryptographic operation: " + target.getName()

/**
 * Incorrect error handling that could lead to information disclosure
 */
from FunctionCall call
where
  call.getTarget().getName().matches("ERR_%") and
  exists(Function parent |
    parent = call.getEnclosingFunction() and
    isOpenSSLCryptoFunction(parent) and
    not exists(ReturnStmt ret | ret.getEnclosingFunction() = parent)
  )
select call, "Error information may not be properly cleared after cryptographic operation"

/**
 * Use of deprecated cryptographic algorithms
 */
from FunctionCall call
where
  call.getTarget().getName().matches("MD5%") or
  call.getTarget().getName().matches("SHA1%") or
  call.getTarget().getName().matches("SSLv%") or
  call.getTarget().getName().matches("TLS1_0%") or
  call.getTarget().getName().matches("TLS1_1%") or
  call.getTarget().getName().matches("SSL3_%")
select call, "Use of deprecated/weak cryptographic algorithm: " + call.getTarget().getName()

/**
 * Missing bounds checking in buffer operations
 */
from FunctionCall call
where
  call.getTarget().getName().matches("memcpy|memmove|memset") and
  exists(Expr sizeExpr |
    sizeExpr = call.getArgument(2) and
    not exists(IfStmt check |
      check.getCondition().getAChild*() = sizeExpr
    )
  ) and
  not call.getFile().getBaseName().matches("%test%")
select call, "Missing bounds checking for memory operation: " + call.getTarget().getName()

/**
 * Potential race conditions in multi-threaded cryptographic operations
 */
from FunctionCall call
where
  call.getTarget().getName().matches("CRYPTO_THREAD%") or
  call.getTarget().getName().matches("OPENSSL_thread%") and
  exists(Function parent |
    parent = call.getEnclosingFunction() and
    isOpenSSLCryptoFunction(parent) and
    not exists(FunctionCall lockCall |
      lockCall.getTarget().getName().matches("CRYPTO_%lock%") and
      lockCall.getEnclosingFunction() = parent
    )
  )
select call, "Potential thread safety issue in cryptographic operation: " + call.getTarget().getName()
