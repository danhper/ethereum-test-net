pragma solidity ^0.4.24;

contract mortal {
    address owner;

    constructor() public {
        owner = msg.sender;
    }

    function kill() public {
        if (msg.sender == owner)
            selfdestruct(owner);
    }
}

contract greeter is mortal {
    string greeting;

    constructor(string _greeting) public {
        greeting = _greeting;
    }

    function greet() public view returns (string) {
        return greeting;
    }
}
