#include <iostream>
class Hidden {
private:
    int secret = 42;
};
int main() {
    Hidden h;
    h.secret = 10;
    return 0;
}
