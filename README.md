# Urbdash

**Urbdash** is an interactive and web-based Python dash application designed to facilitate comparative analysis and benchmarking of global urban networks. The dashboard employs the Global Urban Network dataset, open Attribution 4.0 International (CC BY 4.0) license, hosted on [Figshare](https://doi.org/10.6084/m9.figshare.22124219.v5).

</br>
</br>

<p align="center">
    <img src="https://raw.githubusercontent.com/winstonyym/urbanity/main/images/dashboard.png" width = 1000% alt="Logo">
  <h5 align="center">Urbdash user interface.</h5>
</p>

</br>
</br>

If you use the GUN data or GUN dashboard in your work, please cite:
(*GUN Dataset is currently under review.*)

## Quickstart
*How do I play with this dashboard?*

### Option #1 - Clone local copy
1) Navigate to a location of choice (e.g., Desktop or project folder).
2) Open up a terminal/command prompt and input the following command:

```
$ git clone https://github.com/winstonyym/urbdash.git
$ cd urbdash
$ conda env create -f environment.yml
$ conda activate urbdash-py
$ python app.py
```

3) Done! You can now navigate to the local host server to view and interact with the dashboard. 

### Option #2 - Docker image
For easy access, we provide docker containers for [MacOS](https://hub.docker.com/r/winstonyym/urbdash) and [Windows](https://hub.docker.com/r/winstonyym/urbdash-windows) on Docker Hub. Docker image containers allow users to run virtual environments in their local computer without any further setup. If you do not have Docker installed, please proceed to download Docker Desktop for Mac/Windows at: [Docker](https://docs.docker.com/engine/install/). 

1) Open a terminal / command prompt 
2) Pull the docker image from docker hub

Windows
```
$ docker pull winstonyym/urbdash-windows
```

MacOS
```
$ docker pull winstonyym/urbdash
```

3) Run the Docker image on local port 8050
```
$ docker run -p 8050:8050 winstonyym/urbdash
```

4) Done! You can now navigate to http://localhost:8050 in a web browser of your choice to view the dashboard.


## What can I do with Urbdash?
Users can use the dashboard to examine and compare urban networks through multiple scales---global, city, and local. At the global scale, users can access a variety of network indicators' distributions (such as building footprint proportions and green view index) across cities worldwide. 

This functionality helps cities identify their strengths and weaknesses, offering guidance for improvement. Expanding on the global overview, the dashboard provides features to analyze and compare network structures at the city subzone level.  As an example of equitable planning, planners can pinpoint infrastructure gaps by evaluating population density and civic facility availability across different subzones.

Finally, users can delve into the local scale by directly accessing attributes of nodes and edges. A potential use case would be multi-criteria site assessment which can help planners to quickly identify sites with various characteristics (e.g., low building footprint but high visual complexity). 

## License

`urbdash` was created by winstonyym. Source code is licensed under the terms of the MIT license.
