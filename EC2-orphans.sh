#!/bin/bash

echo "Hello, this script will look for Orphaned Instances and Volumes and Snapshots"

withOwners=`ec2-describe-instances --filter tag-key=*wner | grep INSTANCE | cut -f 2 | sort`
echo $withOwners
