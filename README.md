# Configuration builder

## Description 
Configuration builder that allows you to build configurations as Microsoft.Extension.Configuration.   
Merge the main application settings (appsettings.json) with another json document, environment variables or getting configurations from dotnet user-secrets.

## Install
....

## Usage

Create `appsettings.json`
```json
{
    "flask":{
        "port": 8080,
        "ip": "127.0.0.1",
        "domain":"example.org"
    },
    "appname": "test"
}
```

Create `appsettings.rewrite.json`
```json
{
    "flask":{
        "ip": "0.0.0.0"
    },
}
```
Set environment variables: 
* appname=test-from-env
* flask$$port=8081

Import lib to entrypoint, add json file, and add environmentVariables rewrite.
print actual values.

```python

from configuration_builder import ConfigurationBuilder

# Initialize configuration
configurationBuilder = ConfigurationBuilder()
configurationBuilder.add_json_file("appsettings.json")
configurationBuilder.add_json_file("appsettings.rewrite.json")
configurationBuilder.add_environment_variables()
configuration = configurationBuilder.build()

print(configuration["appname"]) # print: test-from-env
print(configuration["flask"]["port"]) # print: 8081
print(configuration["flask"]["ip"]) # print: 0.0.0.0
print(configuration["flask"]["domain"]) # print: example.org
```