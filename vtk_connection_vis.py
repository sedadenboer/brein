import vtk

def get_positions() -> vtk.vtkPoints:
    """Read the position file.

    Returns:
        vtk.vtkPoints: position points
    """
    # Get the position file location
    position_file_loc = f'data/viz-{simulation_type}/positions/rank_0_positions.txt'

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

def get_areas_list() -> list:
    """Read the area file.
    
    Returns:
        list: area list
    """
    # Get the area file location
    area_file_loc = f'data/viz-{simulation_type}/positions/rank_0_positions.txt'

    # Open the area file
    with open(area_file_loc, 'r') as area_file:
        # Read the lines of the file
        lines = area_file.readlines()
        
        # Create an empty list
        areas = []
        
        # Iterate over the lines
        for line in lines:
            # Skip lines starting with #
            if line.startswith('#'):
                continue
            
            # Split the line into fields
            fields = line.strip().split()
            
            # Extract the area
            area = int(fields[4].split('_')[1])
            
            # Add the area to the list
            areas.append(area)
        
    # Return the area list
    return areas

def get_areas() -> vtk.vtkIntArray:
    """Get the brain areas.

    Returns:
        vtk.vtkIntArray: brain areas
    """
    # Create an empty vtkIntArray object for the brain areas
    areas_array = vtk.vtkIntArray()
    areas_array.SetNumberOfComponents(1)
    areas_array.SetName('Areas')

    # Get the brain areas list and add values to the vtkIntArray object
    areas = get_areas_list()
    for area in areas:
        areas_array.InsertNextValue(area)

    return areas_array

def get_connections_dict(step: int = 1000000) -> dict:
    """Read the connection file.

    Args:
        step (int): simulation step

    Returns:
        dict: connection dictionary
    """
    # Get the connection file location
    connection_infile_loc = f'data/viz-{simulation_type}/network/rank_0_step_{step}_out_network.txt'

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

def get_connections(step: int = 1000000) -> vtk.vtkCellArray:
    """Get the connections.

    Args:
        step (int): simulation step

    Returns:
        vtk.vtkCellArray: connections
    """
    # Get the connections dictionary
    connections_dict = get_connections_dict(step)

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

def create_polydata(points: vtk.vtkPoints,
                    connections: vtk.vtkCellArray,
                    area_mapping: bool) -> (vtk.vtkPolyData, vtk.vtkPolyData):
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
    
    # Get area mapping
    if area_mapping:
        areas = get_areas()
        points_polydata.GetPointData().SetScalars(areas)

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
    glyph_filter = vtk.vtkVertexGlyphFilter()
    glyph_filter.SetInputData(polydata)
    glyph_filter.Update()

    return glyph_filter

def create_point_actor(glyph_filter: vtk.vtkGlyph3D, area_mapping: bool) -> vtk.vtkActor:
    """Create an actor for the points.

    Args:
        glyph_filter (vtk.vtkGlyph3D): glyph filter
        area_mapping (bool): display neuron color based on area

    Returns:
        vtk.vtkActor: point actor
    """
    # Create a mapper 
    point_mapper = vtk.vtkPolyDataMapper()
    point_mapper.SetInputConnection(glyph_filter.GetOutputPort())

    # Appearance settings for the points
    if area_mapping:
        point_mapper.SetScalarRange(0, 47)
        # Set the scalar/color lookup table for the points
        point_mapper.SetLookupTable(get_lut())

    # Create an actor for the points
    point_actor = vtk.vtkActor()
    point_actor.GetProperty().SetPointSize(10)
    point_actor.GetProperty().SetRenderPointsAsSpheres(1)
    # Set color to blue as default
    point_actor.GetProperty().SetColor(0, 0, 1)
    point_actor.SetMapper(point_mapper)

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

def get_lut() -> vtk.vtkLookupTable:
    """Get the lookup table for colors.

    Returns:
        vtk.vtkLookupTable: lookup table
    """
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfColors(256)
    lut.SetHueRange(0, 1)
    lut.SetSaturationRange(1, 1)
    lut.SetValueRange(1, 1)
    lut.SetAlphaRange(1, 1)
    lut.Build()

    return lut

def plot(positions: vtk.vtkPoints,
         connections: vtk.vtkCellArray,
         area_mapping: bool,
         ) -> None:
    """Plot the points and connections.

    Args:
        positions (vtk.vtkPoints): position points
        connections (vtk.vtkCellArray): connections
        area_mapping (bool): display neuron color based on area
    
    Returns:
        None
    """
    # Create polydata for points and connections
    points, lines = create_polydata(positions, connections, area_mapping)
    # Create a glyph filter to display all the points
    glyph_filter = create_glyph_filter(points)

    # Create actors for points and connections
    point_actor = create_point_actor(glyph_filter, area_mapping)
    connection_actor = create_connection_actor(lines)

    # Add axes reference
    axes_actor = vtk.vtkAxesActor()
    axes_actor.SetShaftTypeToCylinder()
    axes_actor.SetXAxisLabelText('X')
    axes_actor.SetYAxisLabelText('Y')
    axes_actor.SetZAxisLabelText('Z')
    axes_actor.SetTotalLength(10, 10, 10)
    axes_actor.SetCylinderRadius(0.02)
    axes_actor.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    axes_actor.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    axes_actor.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    axes_actor.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetVerticalJustificationToBottom()

    # Add title
    text_actor = vtk.vtkTextActor()
    text_actor.SetInput('Brain visualisation with neurons and connections')
    text_actor.GetTextProperty().SetFontSize(24)
    text_actor.GetTextProperty().SetColor(1, 1, 1)
    text_actor.GetTextProperty().BoldOn()
    text_actor.SetDisplayPosition(10, 10)

    # Create a renderer and add the actors
    renderer = vtk.vtkRenderer()
    renderer.AddActor(point_actor)
    renderer.AddActor(connection_actor)
    renderer.AddActor(axes_actor)
    renderer.AddActor(text_actor)
    renderer.ResetCamera()
    renderer.SetBackground(0.32, 0.34, 0.43)

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
    global simulation_type
    simulation_type = 'no-network' # no_network, calcium
    
    # Get the positions and connections
    positions = get_positions()
    connections = get_connections()

    # Plot the points and connections according to settings
    plot(positions=positions,
         connections=connections,
         area_mapping=False)


if __name__ == '__main__':
    main()