/**
 * \brief Finds the greatest common divisor (GCD) of two integers using the Euclidean algorithm
 * 
 * \param a The first integer
 * \param b The second integer
 * \return The GCD of the input integers
 */
int gcd(int a, int b) 
{ 
    if (b == 0) 
        return a; 
    return gcd(b, a % b);   
} 
