foamState
=========

Use ``foamState`` to monitor OpenFOAM jobs.  The jobs to monitor can be
parsed as a list to ``foamState`` or if used on a cluster with Slurm it
can grep the information from the ``squeue``.

To monitor the job in the directory ``test``, simply run::

   $ foamState -dir test

To monitor cases controlled by Slurm for a user run the::

  $ foamState -s -u <user name>

the file that is being parsed needs to be named log.(SOLVERNAME) where the solvername is specified in the controlDict under application