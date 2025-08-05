#include <iostream>
#include <string>
using namespace std;

/**
 * \brief Recursive function to solve a problem by generating all possible combinations of a given string
 * 
 * \param temp An array of strings
 * \param n An integer
 * \param ans An initial answer
 * \return No return value
 */
void solver(string temp[] , int n , string ans){
    if(n == 0){
        cout << ans << endl;
        return;
    }
    int rem = n%10;
    string sol = temp[rem];
    for(int i = 0 ; i < sol.size() ; i++){
        solver(temp , n/10 ,sol[i] + ans );
    }
    
    if(sol.size() == 0){
        solver(temp , n/10 , ans);
    }
    
}
/**
 * \brief Prints the keypad layout for a given number
 * 
 * \param num The number to print the keypad layout for
 * \return None
 */
void printKeypad(int num){
	string* temp = new string[10];
	temp[0] = "";
	temp[1] = "";
	temp[2] = "abc";
	temp[3] = "def";
	temp[4] = "ghi";
	temp[5] = "jkl";
	temp[6] = "mno";
	temp[7] = "pqrs";
	temp[8] = "tuv";
	temp[9] = "wxyz";
    solver(temp , num , "");
}
