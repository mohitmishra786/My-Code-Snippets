#include <iostream>
#include <string>
using namespace std;

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
