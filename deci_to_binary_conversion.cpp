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
 * \brief Converts a decimal integer to its binary representation.
 * \param n The decimal integer to be converted.
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
 * \brief Solves a binary transformation problem by reading an integer from input and processing it using the bin_trans function.
 */
void solve() {
    int n;
    cin >> n;
    bin_trans(n);
    
}

/**
 * \brief Runs a loop of test cases, executing the solve() function for each case.
 * \return None
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
