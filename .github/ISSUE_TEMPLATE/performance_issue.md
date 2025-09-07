---
name: Performance Issue
about: Report performance problems or slow behavior
title: '[PERFORMANCE] '
labels: ['performance', 'needs-investigation']
assignees: []
---

## Performance Issue Description

Describe the performance problem you're experiencing.

## Component Affected

- [ ] Backend API response times
- [ ] Frontend rendering/loading
- [ ] Database queries
- [ ] Demo games performance
- [ ] Real-time dashboard updates
- [ ] Event ingestion

## Current Performance

What is the current performance you're seeing?

- **Metric**: [e.g. response time, load time, memory usage]
- **Current Value**: [e.g. 5 seconds, 500MB]
- **Frequency**: [e.g. always, intermittent, under load]

## Expected Performance

What performance would you expect?

- **Target Metric**: [e.g. < 1 second response time]
- **Reasoning**: [why this target makes sense]

## Environment

- **Data Scale**: [e.g. 10k events, 100 projects]
- **Load**: [e.g. concurrent users, requests per second]
- **Hardware**: [e.g. local dev, cloud instance specs]
- **Browser**: [if frontend-related]

## Reproduction Steps

1. Set up environment with...
2. Generate load by...
3. Measure performance using...
4. Observe slow behavior in...

## Measurements

If you have performance measurements, please share:

```
Paste performance data, logs, or profiler output here
```

## Impact

How does this performance issue affect your use case?

- [ ] Blocks development/testing
- [ ] Poor user experience  
- [ ] Scalability concerns
- [ ] Resource consumption

## Potential Causes

If you have ideas about what might be causing the issue:

- Database query optimization needed
- Frontend bundle size too large
- Memory leaks
- Inefficient algorithms
- Network latency

## Additional Context

Any other relevant information about the performance issue.