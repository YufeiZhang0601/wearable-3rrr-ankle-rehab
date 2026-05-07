# RH1 脚踝康复闭环控制 Demo

当前仓库是一个由 SolidWorks 导出的 ROS 2 机器人描述包。可以直接运行的 demo 是：

```powershell
python scripts\ankle_rehab_closed_loop_demo.py
```

这个脚本会读取 `urdf/rh1.urdf`，把 `joint1`、`joint4`、`joint6` 当作三台虚拟的 XM430-W350-R 舵机，跟踪一个慢速、安全的脚踝康复轨迹，并把闭环反馈数据写入：

```text
demo_output/ankle_rehab_closed_loop.csv
```

## 控制 Demo

默认运动参数比较保守，适合早期脚踝康复测试：

- 背屈/跖屈幅度：`12 deg`
- 内翻/外翻幅度：`6 deg`
- 运动频率：`0.05 Hz`
- 平滑启动时间：`3 s`
- 仿真中使用的力矩限制：`1.2 Nm`
- 仿真中使用的速度限制：`0.8 rad/s`

XM430-W350-R 的堵转力矩只作为硬件上限参考。这个 demo 默认使用更低的患者侧安全力矩限制。真实硬件调参建议按顺序进行：先空载测试，再夹具/假肢测试，最后才在实验室安全流程下进行人体测试。

常用运行命令：

```powershell
python scripts\ankle_rehab_closed_loop_demo.py --duration 60
python scripts\ankle_rehab_closed_loop_demo.py --dorsi-amp-deg 8 --invert-amp-deg 4
python scripts\ankle_rehab_closed_loop_demo.py --torque-limit-nm 0.8 --velocity-limit-rad-s 0.5
```

## URDF 假设

当前 URDF 的主体部分定义了主要的转动关节，文件末尾的 Gazebo 块又额外添加了两个闭链关节。普通 URDF 解析器不会自动求解这些只在 Gazebo 扩展里定义的闭链约束，所以这个第一版 demo 先运行稳定的舵机闭环反馈，而不是完整的闭链动力学仿真。

在进入 Gazebo 或真实硬件控制前，需要注意这些 URDF 问题：

- 所有 revolute joint 当前都是 `effort="0"` 和 `velocity="0"`；
- `package://rh1/meshes/visual/*.STL` 引用的 mesh 文件在当前工作区快照里不存在；
- Gazebo 专用的闭链关节最好在 SDF/Gazebo 里显式建模，或者改成当前物理引擎支持的约束模型。

## 硬件映射

demo 会导出以 `2048` 为中心的 Dynamixel 目标位置 tick，XM430 的位置分辨率大约是 `0.087912 deg/tick`。当前脚本不会向真实电机发送指令。

建议的安全硬件 bring-up 路线：

1. 先运行这个脚本，检查 CSV 里的跟踪误差和目标 tick。
2. 增加 Dynamixel SDK bridge，把三个目标 tick 发送到分别对应 `joint1`、`joint4`、`joint6` 的电机 ID。
3. 读取电机位置和电流反馈，用真实测量值替换脚本里的仿真 measured state。
4. 加入 Vive tracker 的脚踝姿态，作为外环反馈信号。
5. 加入 gait mat 的接触/站立相事件，用于运动 gating、危险载荷时暂停，或在被动 ROM 与 assist-as-needed 模式之间切换。
