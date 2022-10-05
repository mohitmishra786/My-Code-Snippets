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

// ```
//  This problem can be solved as follows.

//     1. Find which of 0,1,2,…,15 is each of the digit in the two-digit hexadecimal notation of N.
//     2. Convert the found digit into a hexadecimal ones 0123456789ABCDEF and print it.
//     3. finding integers a and b between 0 (inclusive) and 16 (exclusive) such that N=16a+b.
// ```

void solve() {
    int n;
    cin >> n;
    
    int a = n/16 , b = n % 16;
    
    if(a <= 9) cout << a;
    else cout << (char)('A' + (a - 10));
    
    if(b <= 9) cout << b;
    else cout << (char)('A' + (b - 10));
}

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
