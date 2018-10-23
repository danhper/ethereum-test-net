## Getting genesis block info as JSON

```
geth attach --datadir data/geth_node1/ --exec "console.log(JSON.stringify(eth.getBlock('latest')))" | head -n1 > geth-output.json
```

## Check JSON diff

```
diff <(jq -S . aleth-output.json) <(jq -S . geth-output.json)
```
