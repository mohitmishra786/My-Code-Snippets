// Less memory taking as we are not storing values anywhere

void subs(string s , string o){
    if(s.length() == 0){
        cout << o << endl;
        return;
    }

    subs(s.substr(1) , o);
    subs(s.substr(1) , o + s[0]);

}
void solve(){
    //Why it has to be me
    string input;
    cin >> input;
    string output = "";
    subs(input , output);
}
