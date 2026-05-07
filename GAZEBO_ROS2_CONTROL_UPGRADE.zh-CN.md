# RH1 Gazebo 与 ros2_control 升级路线

当前已经具备 RViz 可视化视频 demo。下一步如果要做更接近真实机构的物理仿真，需要把“可视化模型”升级成“可受力、可约束、可被控制器驱动”的仿真模型。

## 1. 修正机器人模型

优先处理 `urdf/rh1.urdf` 的仿真问题：

- 补齐 `meshes/visual/*.STL`，否则 Gazebo/RViz 只能使用替代几何体；
- 准备简化版 `meshes/collision/*.STL`，不要直接用高面数视觉 mesh 做碰撞；
- 把 revolute joint 的 `effort="0"` 和 `velocity="0"` 改为合理值；
- 为每个转动关节添加 `dynamics damping/friction`；
- 保留一个原始 CAD 导出版，另建仿真版 `rh1_sim.urdf.xacro` 或 SDF。

## 2. 处理闭链结构

URDF 本质是树结构，不适合直接表达完整闭链机构。当前原始 URDF 末尾用了 Gazebo 扩展补 `joint5_3` 和 `joint7_3`，这只能作为早期尝试。

更稳妥的路线：

- RViz demo：使用开链近似，重点展示控制逻辑和康复轨迹；
- Gazebo demo：使用 SDF 或 Gazebo 支持的约束显式表达闭链；
- 控制验证：先锁定或近似被动支链，确认三台主动 XM430 的轨迹和限幅；
- 高保真验证：再加入真实闭链约束、碰撞和负载。

## 3. 接入 ros2_control

主动关节建议先定义为：

- `joint1`
- `joint4`
- `joint6`

接口建议分阶段：

1. 仿真阶段：`position` command interface，`position/velocity/effort` state interface。
2. 半实物阶段：位置控制仍由 Dynamixel 内部闭环完成，ROS 侧发送目标 tick 或目标角度。
3. 更高级阶段：加入 current/torque 限幅，做 assist-as-needed 或阻抗控制。

## 4. 控制器结构

推荐控制层次：

```text
rehab trajectory
  -> ankle pitch/roll command
  -> three-actuator inverse mapping
  -> safety limiter
  -> ros2_control or Dynamixel SDK bridge
  -> motor feedback
  -> Vive tracker outer-loop feedback
  -> gait mat contact/stance gating
```

安全 limiter 应至少包括：

- 最大脚踝角度限制；
- 最大角速度限制；
- 最大电机电流/力矩限制；
- Vive tracker 数据丢失暂停；
- gait mat 检测到异常站立/接触状态时暂停；
- 急停输入。

## 5. 推荐里程碑

第一阶段：完成当前 RViz 视频 demo，能稳定展示 30-60 秒。

第二阶段：Gazebo 中加载 `rh1_sim.urdf.xacro`，先不追求闭链力学，只验证模型、TF 和控制器能跑。

第三阶段：加入 `ros2_control` 和位置控制器，让 `joint1`、`joint4`、`joint6` 在 Gazebo 中响应轨迹命令。

第四阶段：改用 SDF/约束模型表达闭链，加入碰撞、负载和安全停止。

第五阶段：接入真实 Dynamixel SDK、Vive tracker 和 gait mat，形成半实物闭环实验平台。
