#
#   Copyright (c)
#
#   The Verifiable & Control-Theoretic Robotics (VECTR) Lab
#   University of California, Los Angeles
#
#   Authors: Kenny J. Chen, Ryan Nemiroff, Brett T. Lopez
#   Contact: {kennyjchen, ryguyn, btlopez}@ucla.edu
#

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Set default arguments
    rviz = LaunchConfiguration('rviz', default='false')
    share_dir = LaunchConfiguration('share_dir', default='direct_lidar_inertial_odometry')
    yaml_path = LaunchConfiguration('dlio_yaml_path', default='cfg/dlio.yaml')
    params_yaml_path = LaunchConfiguration('dlio_params_yaml_path', default='cfg/params.yaml')
    pointcloud_topic = LaunchConfiguration('pointcloud_topic', default='points_raw')
    imu_topic = LaunchConfiguration('imu_topic', default='imu_raw')

    # Define arguments
    declare_rviz_arg = DeclareLaunchArgument('rviz', default_value=rviz, description='Launch RViz')
    share_dir_arg = DeclareLaunchArgument(
        'share_dir', default_value=share_dir, description='Path to package share directory'
    )
    declare_dlio_yaml_path_arg = DeclareLaunchArgument(
        'dlio_yaml_path', default_value=yaml_path, description='Path to DLIO configuration file'
    )
    declare_dlio_params_yaml_path_arg = DeclareLaunchArgument(
        'dlio_params_yaml_path', default_value=params_yaml_path, description='Path to DLIO parameters file'
    )
    declare_pointcloud_topic_arg = DeclareLaunchArgument(
        'pointcloud_topic', default_value=pointcloud_topic, description='Pointcloud topic name'
    )
    declare_imu_topic_arg = DeclareLaunchArgument('imu_topic', default_value=imu_topic, description='IMU topic name')

    share_dir_path = FindPackageShare(share_dir)

    # Load parameters
    dlio_yaml_path = PathJoinSubstitution([share_dir_path, yaml_path])
    dlio_params_yaml_path = PathJoinSubstitution([share_dir_path, params_yaml_path])

    tf_remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    # DLIO Odometry Node
    dlio_odom_node = Node(
        package='direct_lidar_inertial_odometry',
        executable='dlio_odom_node',
        output='screen',
        parameters=[dlio_yaml_path, dlio_params_yaml_path],
        remappings=tf_remappings
        + [
            ('pointcloud', pointcloud_topic),
            ('imu', imu_topic),
            ('odom', 'dlio/odom_node/odom'),
            ('pose', 'dlio/odom_node/pose'),
            ('path', 'dlio/odom_node/path'),
            ('kf_pose', 'dlio/odom_node/keyframes'),
            ('kf_cloud', 'dlio/odom_node/pointcloud/keyframe'),
            ('deskewed', 'dlio/odom_node/pointcloud/deskewed'),
        ],
    )

    # DLIO Mapping Node
    dlio_map_node = Node(
        package='direct_lidar_inertial_odometry',
        executable='dlio_map_node',
        output='screen',
        parameters=[dlio_yaml_path, dlio_params_yaml_path],
        remappings=tf_remappings
        + [
            ('keyframes', 'dlio/odom_node/pointcloud/keyframe'),
        ],
    )

    # RViz node
    rviz_config_path = PathJoinSubstitution([share_dir_path, 'launch', 'dlio.rviz'])
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='dlio_rviz',
        arguments=['-d', rviz_config_path],
        output='screen',
        condition=IfCondition(LaunchConfiguration('rviz')),
    )

    return LaunchDescription(
        [
            declare_rviz_arg,
            declare_pointcloud_topic_arg,
            declare_imu_topic_arg,
            declare_dlio_yaml_path_arg,
            declare_dlio_params_yaml_path_arg,
            dlio_odom_node,
            dlio_map_node,
            rviz_node,
        ]
    )
