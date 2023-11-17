import vtk


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


def plot_3d(points: vtk.vtkPoints, connections: dict) -> None:
    """Plot the points and connections in 3D.

    Args:
        points (vtk.vtkPoints): position points
        connections (dict): connection dictionary
    """
    # Create a vtkPolyData object
    polydata = vtk.vtkPolyData()

    # Set the points in the vtkPolyData object
    polydata.SetPoints(points)

    # Create a vtkCellArray object to store the connections
    cell_array = vtk.vtkCellArray()

    # Iterate over the connections
    for key, values in connections.items():
        # Create a vtkIdList object to store the connection indices
        id_list = vtk.vtkIdList()

        # Add the connection indices to the vtkIdList
        for value in values:
            id_list.InsertNextId(value)

        # Add the vtkIdList to the vtkCellArray
        cell_array.InsertNextCell(id_list)

    # Set the connections in the vtkPolyData object
    polydata.SetLines(cell_array)

    # Create a vtkPolyDataMapper object
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)

    # Create a vtkActor object
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Create a vtkRenderer object
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)

    # Create a vtkRenderWindow object
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # Create a vtkRenderWindowInteractor object
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Initialize the interactor and start the rendering loop
    interactor.Initialize()
    render_window.Render()
    interactor.Start()


def main():
    positions = read_positions(SIMULATION[2])
    connections = connection_reader(SIMULATION[2], 0)
    plot_3d(positions, connections)


if __name__ == '__main__':
    main()