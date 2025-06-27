#!/bin/bash

# This command starts a worker that listens for tasks in the Redis queue named 'valkey'.
rq worker --with-scheduler --url redis://valkey:6379
