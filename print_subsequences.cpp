// Less memory taking as we are not storing values anywhere

/**
 * \brief Recursively prints a string in all possible permutations, prepending each character to the output string.
 * \param s The input string.
 * \param o The output string.
 */
void subs(string s , string o){
    if(s.length() == 0){
        cout << o << endl;
        return;
    }

    subs(s.substr(1) , o);
    subs(s.substr(1) , o + s[0]);

}
/**
 * \brief Solves a problem by processing input from the standard input stream and invoking a subsidiary function to perform the actual solution.
 */
void solve(){
    //Why it has to be me
    string input;
    cin >> input;
    string output = "";
    subs(input , output);
}
