## Installation

install repo
(requires python, pip, and setuptools)
```bash
git git@github.com:Devel-Dan/Joby.git
cd Joby
pip install -e .
```


## Usage

### Command Line

```bash
# Use default networks (192.168.1.0/24 and 192.168.2.0/24)
joby_challenge

# Specify custom networks
joby_challenge --network_1 10.0.0.0/24 --network_2 10.1.0.0/24

# Skip specific IP addresses (by last octet)
joby_challenge --skips 1 2 3
```

## Testing

```bash
# Run tests
pytest
```
