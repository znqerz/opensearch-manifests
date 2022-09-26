# Settings configuration

```bash
PUT _cluster/settings
{
  "persistent": {
    "plugins.index_state_management.enabled": true,
    "plugins.index_state_management.job_interval": 60
  }
}
```
