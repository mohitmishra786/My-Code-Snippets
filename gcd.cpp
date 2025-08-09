/**
 * \brief Computes the greatest common divisor of two integers using the Euclidean algorithm.
 * \param a The first integer.
 * \param b The second integer.
 * \return The greatest common divisor of a and b.
 */
int gcd(int a, int b) 
{ 
    if (b == 0) 
        return a; 
    return gcd(b, a % b);  
      
} 
