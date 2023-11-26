import vtk


def get_positions(sim_type: str) -> vtk.vtkPoints:
    """Read the position file.

    Args:
        sim_type (str): simulation type

    Returns:
        vtk.vtkPoints: position points
    """
    # Get the position file location
    position_file_loc = f'data/viz-{sim_type}/positions/rank_0_positions.txt'

    # Create an empty vtkPoints object
    points = vtk.vtkPoints()

    # Open the position file
    with open(position_file_loc, 'r') as position_file:
        # Read the lines of the file
        lines = position_file.readlines()
        
        # Iterate over the lines
        for line in lines:
            # Skip lines starting with #
            if line.startswith('#'):
                continue
            
            # Split the line into fields
            fields = line.strip().split()
            
            # Extract the position coordinates
            x, y, z = map(float, fields[1:4])
            
            # Add the point to the vtkPoints object
            points.InsertNextPoint(x, y, z)
        
        # Print the vtkPoints object
    return points

def get_connections_dict(sim_type: str, step: int) -> dict:
    """Read the connection file.

    Args:
        sim_type (str): simulation type
        step (int): simulation step

    Returns:
        dict: connection dictionary
    """
    # Get the connection file location
    connection_infile_loc = f'data/viz-{sim_type}/network/rank_0_step_{step}_in_network.txt'

    # Create an empty dictionary
    connections_dict = {}

    # Open the connection file
    with open(connection_infile_loc, 'r') as connection_infile:
        # Read the lines of the file
        lines = connection_infile.readlines()
        
        # Iterate over the lines
        for line in lines:
            # Skip empty lines
            if not line or not line.strip():
                continue
            
            # Skip lines starting with #
            if line.startswith('#'):
                continue
            
            # Split the line into fields
            fields = line.strip().split()
            
            # Extract the values
            id1 = int(fields[1]) - 1
            id2 = int(fields[3]) - 1
            
            # Add the connection to the dictionary
            if id1 not in connections_dict:
                connections_dict[id1] = []
            connections_dict[id1].append(id2)
    
    return connections_dict

def get_connections(sim_type: str, step: int) -> vtk.vtkCellArray:
    """Get the connections.

    Args:
        sim_type (str): simulation type
        step (int): simulation step

    Returns:
        vtk.vtkCellArray: connections
    """
    # Get the connections dictionary
    connections_dict = get_connections_dict(sim_type, step)

    # Create an empty vtkCellArray object to store the connections
    connections = vtk.vtkCellArray()

    # Iterate over the connections dictionary to get connected ids
    for id1, id2s in connections_dict.items():
        for id2 in id2s:
            # Create a vtkPolyLine object to store the connection
            polyline = vtk.vtkPolyLine()
            polyline.GetPointIds().SetNumberOfIds(2)

            # Add the ids to the vtkPolyLine object
            polyline.GetPointIds().SetId(0, id1)
            polyline.GetPointIds().SetId(1, id2)
            
            # Add the vtkPolyLine object to the vtkCellArray object
            connections.InsertNextCell(polyline)
            
    return connections

def create_polydata(points: vtk.vtkPoints, connections: vtk.vtkCellArray) -> (
        vtk.vtkPolyData, vtk.vtkPolyData
        ):
    """Create polydata for points and connections.

    Args:
        points (vtk.vtkPoints): points
        connections (vtk.vtkCellArray): connections
    
    Returns:
        vtk.vtkPolyData: points polydata
        vtk.vtkPolyData: connections polydata
    """
    # Create vtkPolyData objects for points and connections
    points_polydata = vtk.vtkPolyData()
    lines_polydata = vtk.vtkPolyData()

    # Set the points and connections for both vtkPolyData objects
    points_polydata.SetPoints(points)
    lines_polydata.SetPoints(points)
    
    # Set the lines for the connections vtkPolyData object
    lines_polydata.SetLines(connections)

    return points_polydata, lines_polydata

def create_glyph_filter(polydata: vtk.vtkPolyData) -> vtk.vtkGlyph3D:
    """Create a glyph filter to display all the points.

    Args:
        polydata (vtk.vtkPolyData): polydata
    
    Returns:
        vtk.vtkGlyph3D: glyph filter
    """
    # Create a sphere source and a glyph filter to represent and display the points
    sphere_source = vtk.vtkSphereSource()
    glyph_filter = vtk.vtkGlyph3D()

    # Set the input data for the glyph filter
    glyph_filter.SetInputData(polydata)
    glyph_filter.SetSourceConnection(sphere_source.GetOutputPort())
    glyph_filter.SetScaleFactor(5)

    return glyph_filter

def create_point_actor(glyph_filter: vtk.vtkGlyph3D) -> vtk.vtkActor:
    """Create an actor for the points.

    Args:
        glyph_filter (vtk.vtkGlyph3D): glyph filter
    
    Returns:
        vtk.vtkActor: point actor
    """
    # Create a mapper and an actor for the points
    point_mapper = vtk.vtkPolyDataMapper()
    point_mapper.SetInputConnection(glyph_filter.GetOutputPort())
    point_actor = vtk.vtkActor()
    point_actor.SetMapper(point_mapper)

    # Appearance settings for the points
    point_actor.GetProperty().SetColor(0.8, 0.2, 0.2)
    return point_actor

def create_connection_actor(polydata: vtk.vtkPolyData) -> vtk.vtkActor:
    """Create an actor for the connections.

    Args:
        polydata (vtk.vtkPolyData): polydata
    
    Returns:
        vtk.vtkActor: connections actor
    """
    # Create a mapper and an actor for the connections
    connection_mapper = vtk.vtkPolyDataMapper()
    connection_mapper.SetInputData(polydata)
    connection_actor = vtk.vtkActor()
    connection_actor.SetMapper(connection_mapper)

    # Appearance settings for the connections
    connection_actor.GetProperty().SetLineWidth(2)
    connection_actor.GetProperty().SetRenderLinesAsTubes(1)
    connection_actor.GetProperty().SetOpacity(0.8)

    return connection_actor

def plot_basic(positions: vtk.vtkPoints, connections: vtk.vtkCellArray) -> None:
    """Plot the points and connections.

    Args:
        positions (vtk.vtkPoints): position points
        connections (vtk.vtkCellArray): connections

    Returns:
        None
    """
    # Create polydata for points and connections
    points, lines = create_polydata(positions, connections)
    # Create a glyph filter to display all the points
    glyph_filter = create_glyph_filter(points)

    # Create actors for points and connections
    point_actor = create_point_actor(glyph_filter)
    connection_actor = create_connection_actor(lines)

    # Create a renderer and add the actors
    renderer = vtk.vtkRenderer()
    renderer.AddActor(point_actor)
    renderer.AddActor(connection_actor)
    renderer.ResetCamera()

    # Create a render window and add the renderer
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # Create an interactor
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    # Render the scene and start the interactor
    render_window.Render()
    render_window_interactor.Start()

def main():
    # Choose the simulation type
    SIMULATION = ['no-network', 'disable', 'stimulus', 'calcium']
    positions = get_positions(SIMULATION[1])
    connections = get_connections(SIMULATION[1], 0)
    plot_basic(positions, connections)


if __name__ == '__main__':
    main()