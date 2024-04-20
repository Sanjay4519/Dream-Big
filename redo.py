import json
from mgpu import DATA_PATH, GEOMETRY, SaveDict
import astra
import numpy as np
from pathlib import Path
from scipy.spatial.transform import Rotation
from matplotlib import pyplot as plt

VOLUME_VOXEL_COUNT = 1024  # [vx]
PROJECTION_NUMBER = 1000  # [n]
DETECTOR_PIXEL_COUNT = 1024  # [px]
DETECTOR_SIZE = 200.  # [mm]
FOD = 1500.  # [mm]
FDD = 2000.  # [mm]


def astra_vector_geometry(number_of_projections: int = PROJECTION_NUMBER, opening_angle: float = 180.,
                          fod: float = FOD, fdd: float = FDD,
                          detector_pitch: float = 1.0) -> np.ndarray:
    # X, Y, Detector Colum, line direction [0,0] -> [0,1] //// [0,0] -> [0,1]
    # Rotation um y-Achse

    detector_transformation = np.eye(4)
    detector_transformation[2, 3] = fdd - fod

    source_transformation = np.eye(4)
    source_transformation[2, 3] = fod

    beta = np.linspace(0.0, opening_angle, number_of_projections, False)
    vector_geometry = np.zeros((number_of_projections, 12))

    for i in range(number_of_projections):
        rotation_matrix = Rotation.from_euler('Y', angles=beta[i], degrees=True)
        transformation = np.eye(4)
        transformation[:3, :3] = rotation_matrix.as_matrix()
        source = transformation @ source_transformation
        detector = transformation @ detector_transformation

        vector_geometry[i, 0:3] = source[:3, 3]
        vector_geometry[i, 3:6] = detector[:3, 3]
        vector_geometry[i, 6:9] = detector[:3, 0] * detector_pitch
        vector_geometry[i, 9:12] = detector[:3, 1] * detector_pitch

    return vector_geometry


def argument_volume(volume: np.ndarray) -> np.ndarray:
    ind_0 = VOLUME_VOXEL_COUNT // 8
    ind_1 = VOLUME_VOXEL_COUNT - ind_0

    ind_2 = VOLUME_VOXEL_COUNT // 6
    ind_3 = VOLUME_VOXEL_COUNT - ind_0

    volume[ind_0:ind_1, ind_0:ind_1, ind_0:ind_1] = 1.
    volume[ind_2:ind_3, ind_2:ind_3, ind_2:ind_3] = 0.

    return volume


def main():
    if not DATA_PATH.exists():
        DATA_PATH.mkdir()

    detector_pitch = DETECTOR_SIZE / float(DETECTOR_PIXEL_COUNT)
    geometry = astra_vector_geometry(detector_pitch=detector_pitch)

    # Create a simple hollow cube phantom
    vol_geom = astra.create_vol_geom(VOLUME_VOXEL_COUNT, VOLUME_VOXEL_COUNT, VOLUME_VOXEL_COUNT)
    cube = np.zeros((VOLUME_VOXEL_COUNT, VOLUME_VOXEL_COUNT, VOLUME_VOXEL_COUNT))
    cube = argument_volume(cube)

    proj_geom = astra.create_proj_geom(GEOMETRY, DETECTOR_PIXEL_COUNT, DETECTOR_PIXEL_COUNT, geometry)
    _, proj_data = astra.create_sino3d_gpu(cube, proj_geom, vol_geom)

    if True:
        plt.imsave(str(DATA_PATH / 'smaple_projection_0.png'), proj_data[:, PROJECTION_NUMBER // 6, :])
        plt.imsave(str(DATA_PATH / 'smaple_projection_1.png'), proj_data[:, PROJECTION_NUMBER // 2, :])

    save_dict = dict()

    save_name_base = DATA_PATH / f'{PROJECTION_NUMBER}_{DETECTOR_PIXEL_COUNT}'

    if not save_name_base.exists():
        save_name_base.mkdir()

    save_vectors = save_name_base / SaveDict.s_vectors
    save_projections = save_name_base / SaveDict.s_projection
    save_volume = save_name_base / SaveDict.s_volume
    save_json = save_name_base / SaveDict.s_json

    np.save(save_vectors, geometry)
    np.save(save_projections, proj_data)
    np.save(save_volume, cube)

    save_dict[SaveDict.vectors] = str(save_vectors)
    save_dict[SaveDict.pixels] = DETECTOR_PIXEL_COUNT
    save_dict[SaveDict.detector_size] = DETECTOR_SIZE
    save_dict[SaveDict.projections] = str(save_projections)
    save_dict[SaveDict.projection_count] = PROJECTION_NUMBER
    save_dict[SaveDict.voxels] = VOLUME_VOXEL_COUNT
    save_dict[SaveDict.geometry] = GEOMETRY
    save_dict[SaveDict.volume] = str(save_volume)

    with open(str(save_json), 'w') as f:
        json.dump(save_dict, f, indent=4)


if __name__ == '__main__':
    main()
