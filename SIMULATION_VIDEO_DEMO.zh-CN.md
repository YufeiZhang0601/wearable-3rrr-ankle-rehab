# RH1 脚踝康复可视化仿真视频 Demo

这个 demo 的目标是先得到一个稳定、可录屏、可解释的仿真视频：RViz 中显示 RH1 机构按脚踝康复轨迹运动，同时控制脚本保存 CSV 日志，便于说明目标角度、反馈误差和 Dynamixel 目标 tick。

## 一键启动 RViz Demo

先构建并 source ROS 2 工作区：

```powershell
colcon build --packages-select rh1
.\install\setup.ps1
```

启动可视化 demo：

```powershell
ros2 launch rh1 ankle_rehab_demo.launch.py
```

默认启动内容：

- `robot_state_publisher`：读取 `urdf/rh1_sim.urdf.xacro` 并发布 TF；
- `ankle_rehab_joint_state_player`：发布 `/joint_states`；
- `rviz2`：加载 `rviz/ankle_rehab_demo.rviz`；
- CSV 日志：默认写到 `demo_output/ankle_rehab_joint_state_player.csv`。

## 为什么使用 `rh1_sim.urdf.xacro`

原始 `urdf/rh1.urdf` 是 SolidWorks 导出的设计模型，但当前工作区缺少 STL mesh 文件，而且 revolute joint 的 `effort` 和 `velocity` 都是 `0`。这会让 Gazebo、`ros2_control` 或轨迹工具无法正确驱动关节。

所以视频 demo 使用 `urdf/rh1_sim.urdf.xacro`：

- 保留原始关节名：`joint1` 到 `joint7`；
- 用简单几何体替代缺失 STL，保证 RViz 能显示；
- 给关节添加非零 `effort`、`velocity`、`dynamics`；
- 先作为可视化/控制演示模型，不声称是高保真闭链动力学模型。

## 录制 30-60 秒视频

推荐录制流程：

1. 打开终端运行：

   ```powershell
   ros2 launch rh1 ankle_rehab_demo.launch.py duration_s:=60 loop:=true
   ```

2. 等 RViz 模型出现后，调整视角，让橙色脚板和三条绿色主动支链都能看到。

3. 用 OBS、Windows Xbox Game Bar 或 PowerPoint 屏幕录制功能录制 30-60 秒。

4. 视频内容建议按这个顺序展示：

   - 先展示完整机构；
   - 展示慢速背屈/跖屈和内翻/外翻运动；
   - 展示终端输出或 CSV 曲线，说明闭环跟踪误差。

如果只想录一次、不循环，可以运行：

```powershell
ros2 launch rh1 ankle_rehab_demo.launch.py duration_s:=45 loop:=false
```

## 可调参数

可以在 launch 命令里覆盖常用参数：

```powershell
ros2 launch rh1 ankle_rehab_demo.launch.py publish_rate_hz:=60 duration_s:=45
```

更细的康复轨迹参数在 `rh1/ankle_rehab_control.py` 的 `default_config()` 中统一管理，包括：

- 背屈/跖屈幅度：`dorsi_amp_deg`
- 内翻/外翻幅度：`invert_amp_deg`
- 运动频率：`frequency_hz`
- 平滑启动时间：`ramp_time_s`
- 控制增益：`kp`、`kd`、`ki`
- 软件安全限幅：`torque_limit_nm`、`velocity_limit_rad_s`

## Gazebo/ros2_control 后续升级路线

可视化视频 demo 完成后，再推进物理仿真：

1. 把实际 STL mesh 放回 `meshes/visual/`，并准备简化 collision mesh。
2. 给主动关节建立 `ros2_control` hardware/interface 配置。
3. 增加 transmission 或 Gazebo/Ignition 支持的 actuator model。
4. 将闭链结构改成 Gazebo/SDF 原生约束，或者先做开链近似模型验证控制器。
5. 加入安全状态机：超角度、超速度、超力矩、Vive tracker 丢失、gait mat 检测异常时暂停。
6. 最后接入真实 Dynamixel SDK，把 CSV 里的目标 tick 替换为真实电机命令。
