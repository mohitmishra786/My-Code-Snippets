#include <iostream>
#include <string>
using namespace std;

/**
 * \brief Recursively generates all possible combinations of the input strings, starting from the last digit of the input integer, and prints the resulting combinations.
 * \param temp The array of input strings.
 * \param n The input integer.
 * \param ans The current combination of strings being built.
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
 * \brief Prints all possible combinations of keypad digits for a given number.
 * \param num The input number for which keypad combinations are to be printed.
 */
void printKeypad(int num){
    /*
    Given an integer number print all the possible combinations of the keypad. You do not need to return anything just print them.
    */
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
