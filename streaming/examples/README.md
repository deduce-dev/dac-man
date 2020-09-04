# Examples

Here we provide 3 example applications that utilize the Deduce-Stream framework
to stream data for real-time analysis.

- Change Detection
- Moving Average
- Image Analysis

## Install requirements

```
pip install -r requirements.txt
```

## Running example

### Streaming source

```
cd /path/to/deduce_stream/examples/<app-folder> # e.g image_analysis

python3 source.py -r blot.lbl.gov -p 6378
```

### Windowed Streaming source
For windowed applications, at least 2 streaming sources are needed (Window-size >= 2)

So let's start two bash sessions:

1st session:
```
cd /path/to/deduce_stream/examples/change_detection

python3 source.py -s 2 -r blot.lbl.gov -p 6378
```

2nd session:
```
cd /path/to/deduce_stream/examples/change_detection

python3 source.py -s 2 -r blot.lbl.gov -p 6378
```

After starting the second streaming session, you should start seeing a similar
output like this:

```
('task:e23ec2f5-9e02-4682-8696-8a03725d67c1', 'datablock:54ff4e58-f753-4bad-84a2-b36683d43090', 'datablock:9e8b2315-dc72-41fc-8f64-fc90190fd54b')
('task:cc20a93e-2ab8-4d29-a5a8-0d5e0be6ce07', 'datablock:ff1d8269-c50d-4308-a156-8745843863a9', 'datablock:348f9ee0-9d84-46dd-a96c-e44dbb4adaed')
('task:cb7704aa-bfef-42dd-b3d6-8d7fba8cfb23', 'datablock:3b4676e4-79e9-4ed5-a197-0d4fd37fbb87', 'datablock:e4bc1cea-fa80-456b-a99c-b9404f856fbd')
('task:a8781b8c-8056-400a-a39a-a84221369b60', 'datablock:6b5e927d-14a6-45ae-ac78-321caa7f6067', 'datablock:141ab56e-d89f-46b3-aafe-bbd150cfcf66')
('task:7e4bf828-4cf5-4e70-9667-bbb2e7ac7895', 'datablock:a95c3c9e-20a4-4186-bb69-19847e3f6bdb', 'datablock:5c5f13d7-da3b-499b-a8f2-c333b781ffd1')
('task:d6971fd1-cdac-4847-b9f0-057934131aa2', 'datablock:ec4900b9-de26-4b36-b558-25eaff487092', 'datablock:bbfcb67b-f3d9-4e4e-b5e1-796d25b93a0e')
('task:72bc1507-9652-4cd7-b504-8587e46e49c4', 'datablock:e2e0b36f-0bc5-44d6-816d-7bd3fcbd8dd2', 'datablock:4ac39605-bfe9-4a5d-a3ac-a262fb540c3f')
```

Each task has a datablock from each streaming source.

If you want to add more streaming sources, just change the window-size `-s` in the command line. 

### Analysis worker
You can add any number of worker sessions as you want. Scaling the number of workers should
be dependent on the task creation rate to be able to perform analysis in real-time.

```
cd /path/to/deduce_stream/examples/<app-folder> # e.g image_analysis

python3 worker.py -r blot.lbl.gov -p 6378
```

Note: Analysis workers are blind to the type of streaming sources (Independent vs Windowed).
