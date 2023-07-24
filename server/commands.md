## Transform the returned array into an object with named keys
```shell
jq 'reduce .[] as $i ({}; .[$i.alias] = {dev_name: $i.dev_name, host: $i.host, is_on: $i.is_on, room: $i.room, zone: $i.zone})' db/mappings.json
```