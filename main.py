import vtk
from vtkmodules.vtkFiltersSources import vtkSphereSource  


SIMULATION = ['no-network', 'disable', 'stimulus', 'calcium']


def read_positions(sim_type: str) -> vtk.vtkPoints:
    """Read the position file.

    Args:
        sim_type (str): simulation type

    Returns:
        vtk.vtkPoints: position points
    """
    # Get the position file location
    position_file_loc = f'data/viz-{sim_type}/positions/rank_0_positions.txt'

    # Open the position file
    with open(position_file_loc, 'r') as position_file:
        # Read the lines of the file
        lines = position_file.readlines()
        
        # Create an empty vtkPoints object
        points = vtk.vtkPoints()
        
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


def connection_reader(sim_type: str, step: int) -> dict:
    """Read the connection file.

    Args:
        sim_type (str): simulation type
        step (int): simulation step

    Returns:
        dict: connection dictionary
    """
    # Get the connection file location
    connection_infile_loc = f'data/viz-{sim_type}/network/rank_0_step_{step}_in_network.txt'

    # Open the connection file
    with open(connection_infile_loc, 'r') as connection_infile:
        # Read the lines of the file
        lines = connection_infile.readlines()
        
        # Create an empty dictionary
        connection_dict = {}
        
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
            value = int(fields[1]) - 1
            key = int(fields[3]) - 1
            
            # Add the value to the list in the dictionary
            if key in connection_dict:
                connection_dict[key].append(value)
            else:
                connection_dict[key] = [value]
        
        # Return the connection dictionary
        return connection_dict

def create_polydata(points, connections):
    """Create a vtkPolyData object with points and connections.

    Args:
        points (vtk.vtkPoints): position points
        connections (dict): connection dictionary

    Returns:
        vtk.vtkPolyData: vtkPolyData object
    """
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)

    lines = vtk.vtkCellArray()
    for point_id, connected_points in connections.items():
        for connected_point_id in connected_points:
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, point_id)
            line.GetPointIds().SetId(1, connected_point_id)
            lines.InsertNextCell(line)

    polydata.SetLines(lines)
    return polydata


def create_glyph_filter(polydata):
    """Create a glyph filter to show individual points.

    Args:
        polydata (vtk.vtkPolyData): vtkPolyData object

    Returns:
        vtk.vtkGlyph3D: glyph filter
    """
    sphere_source = vtkSphereSource()

    glyph_filter = vtk.vtkGlyph3D()
    glyph_filter.SetInputData(polydata)
    glyph_filter.SetSourceConnection(sphere_source.GetOutputPort())
    glyph_filter.SetScaleModeToScaleByScalar()
    glyph_filter.SetScaleFactor(3)

    return glyph_filter


def create_tube_filter(polydata):
    """Create a tube filter to create tubes around the connections.

    Args:
        polydata (vtk.vtkPolyData): vtkPolyData object

    Returns:
        vtk.vtkTubeFilter: tube filter
    """
    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputData(polydata)
    tube_filter.SetRadius(1)

    return tube_filter


def create_renderer(glyph_filter, tube_filter):
    """Create a renderer with actors for tubes and points.

    Args:
        polydata (vtk.vtkPolyData): vtkPolyData object
        glyph_filter (vtk.vtkGlyph3D): glyph filter
        tube_filter (vtk.vtkTubeFilter): tube filter

    Returns:
        vtk.vtkRenderer: renderer
    """
    tube_mapper = vtk.vtkPolyDataMapper()
    tube_mapper.SetInputConnection(tube_filter.GetOutputPort())

    tube_actor = vtk.vtkActor()
    tube_actor.SetMapper(tube_mapper)
    tube_actor.GetProperty().SetColor(1, 1, 1)

    point_mapper = vtk.vtkPolyDataMapper()
    point_mapper.SetInputConnection(glyph_filter.GetOutputPort())

    point_actor = vtk.vtkActor()
    point_actor.SetMapper(point_mapper)
    point_actor.GetProperty().SetColor(0, 0, 1)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(tube_actor)
    renderer.AddActor(point_actor)

    return renderer


def plot_3d(points, connections):
    """Plot the points and connections in 3D.

    Args:
        points (vtk.vtkPoints): position points
        connections (dict): connection dictionary
    """
    polydata = create_polydata(points, connections)
    glyph_filter = create_glyph_filter(polydata)
    tube_filter = create_tube_filter(polydata)
    renderer = create_renderer(glyph_filter, tube_filter)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    render_window.Render()
    render_window_interactor.Start()


def main():
    positions = read_positions(SIMULATION[2])
    connections = connection_reader(SIMULATION[2], 0)
    plot_3d(positions, connections)


if __name__ == '__main__':
    main()