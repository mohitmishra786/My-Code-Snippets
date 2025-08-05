#include <bits/stdc++.h>

using namespace std;

template<typename A, typename B> ostream& operator<<(ostream &os, const pair<A, B> &p) { return os << '(' << p.first << ", " << p.second << ')'; }
template<typename T_container, typename T = typename enable_if<!is_same<T_container, string>::value, typename T_container::value_type>::type> ostream& operator<<(ostream &os, const T_container &v) { os << '{'; string sep; for (const T &x : v) os << sep << x, sep = ", "; return os << '}'; }
void dbg_out() { cerr << endl; }
template<typename Head, typename... Tail> void dbg_out(Head H, Tail... T) { cerr << ' ' << H; dbg_out(T...); }
#ifdef LOCAL
#define dbg(...) cerr << "(" << #__VA_ARGS__ << "):", dbg_out(__VA_ARGS__)
#else
#define dbg(...)
#endif

#define ar array
#define ll long long
#define ld long double
#define sza(x) ((int)x.size())
#define all(a) (a).begin(), (a).end()

const int MAX_N = 1e5 + 5;
const ll MOD = 1e9 + 7;
const ll INF = 1e9;
const ld EPS = 1e-9;

/**
 * \brief Converts an integer to its binary representation
 * 
 * \param n The integer to convert
 * \return None
 */
void bin_trans(int n){
    int i = 0;
    int bin[32];
    
    while(n > 0){
        bin[i] = n % 2;
        n /= 2;
        i++;
    }
    
    for(int j = i - 1 ; j >=0 ; j--){
        cout << bin[j];
    }
}

/**
 * \brief Reads an integer and calls the bin_trans function
 * 
 * \param n An integer
 */
void solve() {
    int n;
    cin >> n;
    bin_trans(n);
    
}

/**
 * \brief Main function that calls the solve() function for a specified number of test cases
 * 
 * \param tc The number of test cases
 * \return No explicit return value, as it is a void function
 */
int main() {
    ios_base::sync_with_stdio(0);
    cin.tie(0); cout.tie(0);
    int tc = 1;
    // cin >> tc;
    for (int t = 1; t <= tc; t++) {
        // cout << "Case #" << t << ": ";
        solve();
    }
}
