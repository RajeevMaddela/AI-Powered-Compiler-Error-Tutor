#include <iostream>
#include <string>

class BankAccount {
private:
    std::string owner;
    double balance;

public:
    BankAccount(const std::string& name, double initial) : owner(name), balance(initial) {}

    void deposit(double amount) {
        if (amount > 0.0) {
            balance += amount;
        }
    }

    double getBalance() const {
        return balance;
    }

    std::string getOwner() const {
        return owner;
    }
};

int main() {
    BankAccount account("Alice", 150.0);
    account.deposit(75.5);
    std::cout << account.getOwner() << " has balance: " << account.getBalance() << std::endl;
    return 0;
}
