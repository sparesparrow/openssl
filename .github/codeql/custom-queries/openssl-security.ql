/**
 * @name OpenSSL-specific security queries
 * @description Custom security queries for OpenSSL cryptographic library
 * @kind problem
 * @id openssl/security
 * @problem.severity error
 * @precision high
 * @tags security
 */

import cpp
import semmle.code.cpp.dataflow.DataFlow
import semmle.code.cpp.security.Cryptographic

/**
 * Check for potential buffer overflows in OpenSSL memory functions
 */
predicate isOpenSSLEVPFunction(FunctionCall call) {
  call.getTarget().getName().matches("EVP_%") or
  call.getTarget().getName().matches("EVP_%_%")
}

from FunctionCall call, Expr size
where 
  isOpenSSLEVPFunction(call) and
  call.getAnArgument() = size and
  size.getType().(IntegerType).getSize() < 32
select call, "Potential buffer overflow: OpenSSL EVP function with small size argument"




