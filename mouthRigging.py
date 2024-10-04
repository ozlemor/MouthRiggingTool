import maya.cmds as cmds
from builtins import zip
import maya.mel as mel
import math

model_tool = None
first_tool = None
second_tool = None
dup_model = None
cheek_tool = None
cheek_vtx = None
created_joints = []


def create_joint(*args):
    neck_jnt = cmds.joint(name = "neck_jnt", r = 0.2)

    head_jnt = cmds.joint(name = "head_jnt", radius = 0.2)
    cmds.setAttr(head_jnt + ".translateY", 2)
        
    head_tip_jnt = cmds.joint(name = "head_tip_jnt", radius = 0.2)
    cmds.setAttr(head_tip_jnt + ".translateY", 2)
        
    jaw_jnt = cmds.joint(name = "jaw_jnt", radius = 0.2)
    cmds.parent(jaw_jnt, world = True)
    cmds.parent(jaw_jnt, head_jnt)
    cmds.setAttr(jaw_jnt + ".translateY", 0)
    cmds.setAttr(jaw_jnt + ".translateZ", 0.5)
        
    jaw_tip_jnt = cmds.joint(name = "jaw_tip_jnt", radius = 0.2)
    cmds.setAttr(jaw_tip_jnt + ".translateZ", 2)
    
    skel_grp = cmds.group(empty = True, n = "Skel_grp")
    cmds.parent(neck_jnt, skel_grp)
    noTransform_grp = cmds.group(empty = True, name = "noTransform_grp")
    cmds.parent(skel_grp, noTransform_grp)
    setDrv_jnt_grp = cmds.group(empty = True, name = "setDrv_jnt_grp")
    cmds.group(empty = True, name = "crv_loft_grp")
    cmds.parent(setDrv_jnt_grp, "noTransform_grp")
    cmds.parent("crv_loft_grp", "noTransform_grp")
    return skel_grp


def build_joints(*args):
    global model_tool, dup_model, skel_grp  # Add these global variables

    model_to_duplicate = cmds.textField(model_tool, query = True, text = True)

    if model_to_duplicate:
        skel_grp = create_joint()  # Call the create_joint function to create joints
        dup_model = cmds.duplicate(model_to_duplicate, n = "head_skin")[0]
        cmds.xform(dup_model, cp = True)
        cmds.delete(dup_model, ch = True)
        cmds.hide(dup_model)
        head_geo_grp = cmds.group(empty = True, n = "Head_geo_grp")
        cmds.parent(dup_model, head_geo_grp)

        skeleton_data = cmds.listRelatives(skel_grp, allDescendents = True, type = "joint")
        print(skeleton_data)

        if skeleton_data:
            cmds.blendShape(dup_model, model_to_duplicate, n = "kafa_bs", en = 1, tc = True, w = [(0, 1.0)])
        else:
            cmds.warning("No joints found in the skeleton group.")
    else:
        cmds.warning("No model selected for duplication.")

def create_cheek_bones(*args):
	skin_bones_grp = cmds.group(name = "skin_jnt_grp", empty =True)

	cheek_01_bones = cmds.joint(name = "cheek_01_jnt_skin", radius = 0.4)
	cmds.parent(cheek_01_bones, world = True)
	cmds.setAttr(cheek_01_bones + ".translateX", -3)

	cheek_02_bones = cmds.joint(name = "cheek_02_jnt_skin", radius = 0.4)
	cmds.parent(cheek_02_bones, world = True)
	cmds.setAttr(cheek_02_bones + ".translateX", -1)
	cmds.setAttr(cheek_02_bones + ".translateY", 0.5)

	cheek_03_bones = cmds.joint(name = "cheek_03_jnt_skin", radius = 0.4)
	cmds.parent(cheek_03_bones, world = True)
	cmds.setAttr(cheek_03_bones + ".translateX", -1)
	cmds.setAttr(cheek_03_bones + ".translateY", -1)

	cheek_04_bones = cmds.joint(name = "cheek_04_jnt_skin", radius = 0.4)
	cmds.parent(cheek_04_bones, world = True)
	cmds.setAttr(cheek_04_bones + ".translateX", 1)
	cmds.setAttr(cheek_04_bones + ".translateY", -1)
	
	cheek_05_bones = cmds.joint(name = "cheek_05_jnt_skin", radius = 0.4)
	cmds.parent(cheek_05_bones, world = True)
	cmds.setAttr(cheek_05_bones + ".translateX", 1)
	cmds.setAttr(cheek_05_bones + ".translateY", 1)

	cmds.parent(cheek_01_bones, skin_bones_grp)
	cmds.parent(cheek_02_bones, skin_bones_grp)
	cmds.parent(cheek_03_bones, skin_bones_grp)
	cmds.parent(cheek_04_bones, skin_bones_grp)
	cmds.parent(cheek_05_bones, skin_bones_grp)

	cmds.setAttr(skin_bones_grp + ".translateX", 2)
	cmds.setAttr(skin_bones_grp + ".translateY", 5)
	cmds.parent(skin_bones_grp, "noTransform_grp")

def create_control_and_skin(*args):
	skel_grp = "Skel_grp"
	skeleton_data = cmds.listRelatives(skel_grp, allDescendents = True, type = "joint")
	head_skin = cmds.skinCluster(dup_model, skeleton_data, n = "head_skin_cluster", tsb = True)

	skel_ctrl_grp = []

	for skel in skeleton_data:
		if skel == "jaw_jnt":
			joint_position = cmds.xform(skel, query = True, worldSpace = True, translation = True)
			jaw_ctrl_name = skel.replace("_jnt", "_ctrl")
			jaw_ctrl = cmds.circle(name = jaw_ctrl_name, radius = 1)

			cmds.xform(jaw_ctrl, worldSpace =True, translation = joint_position)

			jaw_ctrl_grp = cmds.group(jaw_ctrl, name = jaw_ctrl_name + "_grp")
			cmds.delete(cmds.parentConstraint(skel, jaw_ctrl))
			cmds.setAttr("jaw_ctrl.rotateX", 90)
			cmds.makeIdentity(jaw_ctrl, apply = True, translate = True, rotate = True, scale = True)
			cmds.parentConstraint(jaw_ctrl, skel, mo = True)
			skel_ctrl_grp.append(jaw_ctrl_grp)
		
		elif skel == "head_jnt":
			joint_position = cmds.xform(skel, query = True, worldSpace = True, translation = True)
			head_ctrl_name = skel.replace("_jnt", "_ctrl")
			head_ctrl = cmds.circle(name = head_ctrl_name, radius = 1)

			cmds.xform(head_ctrl, worldSpace =True, translation = joint_position)

			head_ctrl_grp = cmds.group(head_ctrl, name = head_ctrl_name + "_grp")
			cmds.delete(cmds.parentConstraint(skel, head_ctrl))
			cmds.setAttr("head_ctrl.rotateX", 90)
			cmds.makeIdentity(head_ctrl, apply = True, translate = True, rotate = True, scale = True)
			cmds.parentConstraint(head_ctrl, skel, mo = True)
			skel_ctrl_grp.append(head_ctrl_grp)
	for ctrl in skel_ctrl_grp:
		if ctrl == "jaw_ctrl_grp":
			cmds.parent("jaw_ctrl_grp", "head_ctrl")

def find_closest_vertex(joint_position, mesh_name):
    closest_vertex = None
    if mesh_name is not None:
        vertices = cmds.ls(mesh_name + '.vtx[*]', fl=True)
        closest_vertex = None
        min_distance = float('inf')
        
        for vertex in vertices:
            vertex_position = cmds.pointPosition(vertex, world=True)
            distance = sum((a-b)**2 for a, b in zip(vertex_position, joint_position))**0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_vertex = vertex
    else:
        print("Error 'mesh_name'is None. Check your variable assignment")    
    return closest_vertex

def skin_joint(joint_grp):

    joints = cmds.listRelatives(joint_grp, ad = True, type = "joint")

    for joint in joints:
        print (joint)
        cmds.skinCluster("head_skin_cluster", edit = True, ai = joint)

        joint_position = cmds.xform(joint, query = True, ws = True, t = True)
        print(joint_position)

    closest_vertex = find_closest_vertex(joint_position, dup_model)
    print(closest_vertex)
    
    #history = cmds.listHistory(dup_model)
    #print(history)

    skin_cluster = cmds.listConnections(dup_model, type='skinCluster')
    print(skin_cluster)
    
    if skin_cluster:
        skin_cluster = skin_cluster[0]

    # Edit the skin cluster to add the influence
        cmds.skinCluster(skin_cluster, edit=True, ai=joint)
        cmds.skinPercent(skin_cluster, str(closest_vertex), transformValue=[(str(joint), 1.0)])
    else:
        cmds.warning("Skin cluster not found for the duplicated mesh.")
def create_controller_and_joint(target_position, suffix, prefix, ctrl_grp, jnt_grp):
    created_circle = {}
    created_joint = {}
    main_controller = cmds.circle(r = 0.3, name = f"{prefix}_{suffix}_ctrl")[0]

    main_joint = cmds.joint(name = f"{prefix}_{suffix}_jnt")
    cmds.xform(main_joint, centerPivots = True)
    cmds.delete(main_joint, ch = True)
    cmds.parent(main_joint, jnt_grp)

    if target_position not in created_circle:
        cmds.xform(main_controller, worldSpace = True, translation = target_position)
        cmds.makeIdentity(main_controller, apply = True, translate = True, rotate = True, scale = True)
        cmds.xform(main_joint, worldSpace = True, translation = target_position)
        created_circle[target_position] = main_controller
        created_joint[target_position] = main_joint
        
        if "tri" in main_controller:
            process_tri_controller(main_controller, target_position, suffix, prefix, ctrl_grp)
        elif "corner" in main_controller:
            process_corner_controller(main_controller, target_position, suffix, prefix, ctrl_grp)
        elif "A" in main_controller or "B" in main_controller:
            process_A_B_controller(main_controller, target_position,suffix, prefix, ctrl_grp)
        elif "A2" in main_controller or "B2" in main_controller:
            process_A2_B2_controller(main_controller, target_position, suffix, prefix, ctrl_grp)
        elif "top" in main_controller or "down" in main_controller:
            process_top_down_controller(main_controller, target_position, suffix, prefix, ctrl_grp)
        else:
            process_default_controller(main_controller, target_position, suffix, prefix, ctrl_grp)

        cmds.makeIdentity(main_controller, apply = True, t = True, r = True, s = True, n = False, pn = True)
        cmds.delete(main_controller, ch = True)

        cmds.parentConstraint(main_controller, main_joint, mo = True, w = 1)

    cmds.rename(main_controller, f"{prefix}_{suffix}_ctrl")
    cmds.rename(main_joint, f"{prefix}_{suffix}_jnt")

def process_tri_controller(main_controller, target_position, suffix, prefix, ctrl_grp):
    ctrl_sec_grp = cmds.group(name = f"{prefix}_{suffix}_ctrl_grp", empty = True)
    cmds.xform(ctrl_sec_grp, ws = True, translation = target_position)
    
    tri_ctrl_grp = cmds.group(name = f"{prefix}_{suffix}_ctrl_side_grp", empty = True)
    cmds.xform(tri_ctrl_grp, ws = True, translation = target_position) 
    
    cmds.parent(main_controller, tri_ctrl_grp)
    cmds.parent(tri_ctrl_grp, ctrl_sec_grp)
    cmds.parent(ctrl_sec_grp, ctrl_grp)

    pivot_pos = cmds.xform(main_controller, q = True, ws = True, rotatePivot = True)
    if "L_upperLip" in main_controller or "L_lowerLip" in main_controller:
    	cmds.move(0.5, 0.3, 0.5, main_controller) if "L_upperLip" in main_controller or "L_lowerLip" in main_controller else cmds.move(-0.5, -0.3, 0.5, main_controller)
    	cmds.setAttr(main_controller + ".scaleX", 0.3)
    	cmds.setAttr(main_controller + ".scaleY", 0.3)
    	cmds.setAttr(main_controller + ".scaleZ", 0.3)
    	cmds.xform(main_controller, ws = True, pivots = (pivot_pos[0], pivot_pos[1], pivot_pos[2]))

def process_corner_controller(main_controller, target_position, suffix, prefix, ctrl_grp):
    corner_ctrl_grp = cmds.group(name = f"{prefix}_{suffix}_corner_grp", empty = True)
    cmds.xform(corner_ctrl_grp, ws = True, translation = target_position)
    
    cmds.addAttr(main_controller, longName = "eyeInfluence", attributeType = "double", defaultValue = 0.2, minValue = 0, maxValue = 2)
    cmds.setAttr(main_controller + ".eyeInfluence", keyable = True)

    cmds.addAttr(main_controller, longName = "eyeOuterInfluence", attributeType = "double", defaultValue = 0.2, minValue = 0, maxValue = 2)
    cmds.setAttr(main_controller + ".eyeOuterInfluence", keyable = True)

    cmds.addAttr(main_controller, longName = "noseInfluence", attributeType = "double", defaultValue = 0.1, minValue = 0, maxValue = 2)
    cmds.setAttr(main_controller + ".noseInfluence", keyable = True)

    cmds.addAttr(main_controller, longName = "cheek", attributeType = "double", defaultValue = 0.75, minValue = 0, maxValue = 2)
    cmds.setAttr(main_controller + ".cheek", keyable = True)

    cmds.addAttr(main_controller, longName = "cheekJaw", attributeType = "double", defaultValue = 0.5, minValue = 0, maxValue = 2)
    cmds.setAttr(main_controller + ".cheekJaw", keyable = True)

    cmds.addAttr(main_controller, longName = "cheekUp", attributeType = "double", defaultValue = 0.5, minValue = 0, maxValue = 2)
    cmds.setAttr(main_controller + ".cheekUp", keyable = True)

    cmds.addAttr(main_controller, longName = "cheekEye", attributeType = "double", defaultValue = 0.5, minValue = 0, maxValue = 2)
    cmds.setAttr(main_controller + ".cheekEye", keyable = True)

    cmds.parent(main_controller, corner_ctrl_grp)
    cmds.parent(corner_ctrl_grp, ctrl_grp)

    pivot_pos = cmds.xform(main_controller, q = True, ws = True, rotatePivot = True)
    cmds.move(0, 0.15, 0.3, main_controller, relative = True)
    cmds.setAttr(main_controller + ".scaleX", 0.6)
    cmds.setAttr(main_controller + ".scaleY", 0.6)
    cmds.setAttr(main_controller + ".scaleZ", 0.6)
    cmds.xform(main_controller, ws = True, pivots = (pivot_pos[0], pivot_pos[1], pivot_pos[2]))

def process_top_down_controller(main_controller, target_position, suffix, prefix, ctrl_grp):
    ctrl_sec_grp = cmds.group(name = f"{prefix}_{suffix}_ctrl_grp", empty = True)
    cmds.xform(ctrl_sec_grp, ws = True, translation = target_position)
    
    cmds.parent(main_controller, ctrl_sec_grp)
    cmds.parent(ctrl_sec_grp, ctrl_grp)

    pivot_pos = cmds.xform(main_controller, q = True, ws = True, rotatePivot = True)
    cmds.move(0, 0.5, 0.6, main_controller) if "top" in main_controller else cmds.move(0, -0.5, 0.6, main_controller) 
    cmds.setAttr(main_controller + ".scaleX", 0.7)
    cmds.setAttr(main_controller + ".scaleY", 0.7)
    cmds.setAttr(main_controller + ".scaleZ", 0.7)
    cmds.xform(main_controller, ws = True, pivots = (pivot_pos[0], pivot_pos[1], pivot_pos[2]))

def process_A_B_controller(main_controller, target_position, suffix, prefix, ctrl_grp):
    ctrl_sec_grp = cmds.group(name = f"{prefix}_{suffix}_ctrl_grp", empty = True)
    cmds.xform(ctrl_sec_grp, ws = True, translation = target_position)

    ctrl_sec_02_grp = cmds.group(name = f"{prefix}_{suffix}_ctrl_02_grp", empty = True)
    cmds.xform(ctrl_sec_02_grp, ws = True, translation = target_position) 

    cmds.parent(main_controller, ctrl_sec_02_grp)
    cmds.parent(ctrl_sec_02_grp, ctrl_sec_grp)
    cmds.parent(ctrl_sec_grp, ctrl_grp)

    pivot_pos = cmds.xform(main_controller, q = True, ws = True, rotatePivot = True)
    cmds.move(0, 0.3, 0.5, main_controller) if "L_upperLip" in main_controller or "R_upperLip" in main_controller else cmds.move(0, -0.3, 0.5, main_controller) 
    cmds.setAttr(main_controller + ".scaleX", 0.4)
    cmds.setAttr(main_controller + ".scaleY", 0.4)
    cmds.setAttr(main_controller + ".scaleZ", 0.4)
    cmds.xform(main_controller, ws = True, pivots = (pivot_pos[0], pivot_pos[1], pivot_pos[2]))

def process_A2_B2_controller(main_controller, target_position, suffix, prefix, ctrl_grp):
    ctrl_sec_grp = cmds.group(name = f"{prefix}_{suffix}_ctrl_grp", empty = True)
    cmds.xform(ctrl_sec_grp, ws = True, translation = target_position)

    ctrl_sec_02_grp = cmds.group(name = f"{prefix}_{suffix}_ctrl_02_grp", empty = True)
    cmds.xform(ctrl_sec_02_grp, ws = True, translation = target_position)

    ctrl_sec_03_grp = cmds.group(name = f"{prefix}_{suffix}_ctrl_03_grp", empty = True)
    cmds.xform(ctrl_sec_03_grp, ws = True, translation = target_position) 

    cmds.parent(main_controller, ctrl_sec_03_grp)
    cmds.parent(ctrl_sec_03_grp, ctrl_sec_02_grp)
    cmds.parent(ctrl_sec_02_grp, ctrl_sec_grp)
    cmds.parent(ctrl_sec_grp, ctrl_grp)

    pivot_pos = cmds.xform(main_controller, q = True, ws = True, rotatePivot = True)
    cmds.move(0, 0.3, 0.5, main_controller) if "L_upperLip" in main_controller or "R_upperLip" in main_controller else cmds.move(0, -0.3, 0.5, main_controller) 
    cmds.setAttr(main_controller + ".scaleX", 0.4)
    cmds.setAttr(main_controller + ".scaleY", 0.4)
    cmds.setAttr(main_controller + ".scaleZ", 0.4)
    cmds.xform(main_controller, ws = True, pivots = (pivot_pos[0], pivot_pos[1], pivot_pos[2]))

def process_default_controller(main_controller, target_position, suffix, prefix, ctrl_grp):
    ctrl_sec_grp = cmds.group(name = f"{prefix}_{suffix}_ctrl_grp", empty = True)
    cmds.xform(ctrl_sec_grp, ws = True, translation = target_position)
    
    cmds.parent(main_controller, ctrl_sec_grp)
    cmds.parent(ctrl_sec_grp, ctrl_grp)

    pivot_pos = cmds.xform(main_controller, q = True, ws = True, rotatePivot = True)
    cmds.move(0, 0.3, 0.3, main_controller) if "L_upperLip" in main_controller or "R_upperLip" in main_controller or "midLip" in main_controller else cmds.move(0, -0.3, 0.3, main_controller) 
    cmds.setAttr(main_controller + ".scaleX", 0.5)
    cmds.setAttr(main_controller + ".scaleY", 0.5)
    cmds.setAttr(main_controller + ".scaleZ", 0.5)
    cmds.xform(main_controller, ws=True, pivots=(pivot_pos[0], pivot_pos[1], pivot_pos[2]))

def createFol(num_edges, loft):
	if loft[0] == "loft_upper_created":
	    fol_grp = cmds.group(em = True, name = "upper_follicle_grp")
	    fol_jnt_group = cmds.group(em = True, name = "upper_joint_follicle_grp")
	    upper_ribbon_grp = cmds.group(em = True, name = "upper_ribbon_grp")
	    pV_num = 0.0
	    for num in range(num_edges + 1):
	        follicleShp = cmds.createNode('follicle')
	        follicleTransform = cmds.listRelatives(follicleShp, parent = True)[0]
	        cmds.connectAttr(loft[0] + '.worldMatrix[0]', follicleShp + '.inputWorldMatrix')
	        cmds.connectAttr(loft[0] + '.local', follicleShp + '.inputSurface')
	        cmds.setAttr(follicleShp + ".parameterU", 0.5)
	        cmds.setAttr(follicleShp + ".parameterV", pV_num)
	        pV_num += 1.0 / num_edges if num_edges else 0  # Prevent division by zero
	        cmds.connectAttr(follicleShp + '.outRotate', follicleTransform + '.rotate')
	        cmds.connectAttr(follicleShp + '.outTranslate', follicleTransform + '.translate')
	        cmds.setAttr(follicleShp + '.simulationMethod', 2)
	        cmds.parent(follicleShp, fol_grp)
	        joint_name = cmds.joint(radius = 0.2)
	        cmds.parent(joint_name, world = True)
	        fol_joint_position = cmds.xform(follicleTransform, query = True, worldSpace = True, translation = True)
	        cmds.xform(joint_name, worldSpace = True, translation = fol_joint_position)
	        cmds.parentConstraint(follicleTransform, joint_name, maintainOffset = True, weight = 1)
	        cmds.parent(joint_name, fol_jnt_group)
	    cmds.parent(fol_grp, upper_ribbon_grp)
	    cmds.parent(fol_jnt_group, upper_ribbon_grp)
	    skin_joint(fol_jnt_group)

	    lip_all_grp = cmds.group(name = "Lip_All_grp", empty = True)

	    upper_ctrl_grp = cmds.group(em = True, n = "upperLip_all_ctrl_grp")
	    upper_sec_ctrl_grp = cmds.group(name = "upperLip_sec_ctrl_grp")
	    
	    upper_jnt_grp = cmds.group(em = True, n = "upperLip_jnt_grp")
	    upper_sec_jnt_grp = cmds.group(name = "upperLip_sec_jnt_grp", empty = True)
	    cmds.parent(upper_sec_jnt_grp, upper_jnt_grp)

	    cmds.parent(upper_ctrl_grp, lip_all_grp)
	    cmds.parent(upper_sec_ctrl_grp, upper_ctrl_grp)
	    cmds.parent("upperLip_jnt_grp", "noTransform_grp")
	    cmds.parent("upper_ribbon_grp", "noTransform_grp")
	    cmds.parent("Lip_All_grp", "head_ctrl")

	    all_follicles = cmds.listRelatives(fol_grp, c = True) or []

	    created_circle = {}
	    created_joint = {}

	    mid_index = len(all_follicles)//2
	    for index, follicle in enumerate(all_follicles):
	    	if index == 0:
	    		create_controller_and_joint(cmds.getAttr(follicle + ".translate")[0], "A", "L_upperLip_corner", lip_all_grp, upper_sec_jnt_grp)
    		if index == 2:
    			create_controller_and_joint(cmds.getAttr(follicle + ".translate")[0], "A_tri", "L_upperLip", upper_sec_ctrl_grp, upper_sec_jnt_grp)
    		if index == len(all_follicles) - 1:
    			create_controller_and_joint(cmds.getAttr(follicle + ".translate")[0], "B", "R_upperLip_corner", lip_all_grp, upper_sec_jnt_grp)
    		if index == mid_index:
    			create_controller_and_joint(cmds.getAttr(follicle + ".translate")[0], "mid", "midLip_upper", upper_sec_ctrl_grp, upper_sec_jnt_grp)
    			create_controller_and_joint(cmds.getAttr(follicle + ".translate")[0], "top", "upperLip", upper_sec_ctrl_grp, upper_sec_jnt_grp)
    		if index == len(all_follicles) - 2:
	        	create_controller_and_joint(cmds.getAttr(follicle + ".translate")[0], "B_tri", "R_upperLip", upper_sec_ctrl_grp, upper_sec_jnt_grp)

	    num_elements_each_side = (len(all_follicles)-1)//2
	    print(num_elements_each_side)
	    mid_upper = ((len(all_follicles) - 3) + mid_index) // 2
	    mid_lower = (3 + mid_index)//2

	    mid_between_mid_and_mid_lower = (mid_index + mid_lower) // 2
	    mid_between_mid_and_mid_upper = (mid_index + mid_upper) // 2
	    mid_between_mid_lower_and_end = (mid_lower + 1) // 2 
	    mid_between_mid_upper_and_end = (mid_upper + (len(all_follicles) - 1)) // 2

	    for i in range(2, num_elements_each_side -2):
	        index_right = mid_index + i
	        index_left = mid_index - i
	        if index_left == mid_lower:
        		create_controller_and_joint(cmds.getAttr(all_follicles[index_left] + ".translate")[0], "A2_sec", "L_upperLip", upper_sec_ctrl_grp, upper_sec_jnt_grp)
        		create_controller_and_joint(cmds.getAttr(all_follicles[mid_between_mid_and_mid_lower] + ".translate")[0], "A1_sec", "L_upperLip", upper_sec_ctrl_grp, upper_sec_jnt_grp)
        		create_controller_and_joint(cmds.getAttr(all_follicles[mid_between_mid_lower_and_end] + ".translate")[0], "A_sec", "L_upperLip", upper_sec_ctrl_grp, upper_sec_jnt_grp)
        	if index_right == mid_upper:
        		create_controller_and_joint(cmds.getAttr(all_follicles[index_right] + ".translate")[0], "B2_sec", "R_upper", upper_sec_ctrl_grp, upper_sec_jnt_grp)
        		create_controller_and_joint(cmds.getAttr(all_follicles[mid_between_mid_and_mid_upper] + ".translate")[0], "B1_sec", "R_upperLip", upper_sec_ctrl_grp, upper_sec_jnt_grp)
        		create_controller_and_joint(cmds.getAttr(all_follicles[mid_between_mid_upper_and_end] + ".translate")[0], "B_sec", "R_upperLip", upper_sec_ctrl_grp, upper_sec_jnt_grp)

	if loft[0] == "loft_lower_created":
	    fol_grp = cmds.group(em = True, name = "lower_follicle_grp")
	    fol_jnt_group = cmds.group(em = True, name = "lower_joint_follicle_grp")
	    lower_ribbon_grp = cmds.group(em = True, name = "lower_ribbon_grp")
	    pV_num = 0.0
	    for num in range(num_edges + 1):
	        follicleShp = cmds.createNode('follicle')
	        follicleTransform = cmds.listRelatives(follicleShp, parent = True)[0]
	        cmds.connectAttr(loft[0] + '.worldMatrix[0]', follicleShp + '.inputWorldMatrix')
	        cmds.connectAttr(loft[0] + '.local', follicleShp + '.inputSurface')
	        cmds.setAttr(follicleShp + ".parameterU", 0.5)
	        cmds.setAttr(follicleShp + ".parameterV", pV_num)
	        pV_num += 1.0 / num_edges if num_edges else 0  # Prevent division by zero
	        cmds.connectAttr(follicleShp + '.outRotate', follicleTransform + '.rotate')
	        cmds.connectAttr(follicleShp + '.outTranslate', follicleTransform + '.translate')
	        cmds.setAttr(follicleShp + '.simulationMethod', 2)
	        cmds.parent(follicleShp, fol_grp)
	        joint_name = cmds.joint(radius = 0.2)
	        cmds.parent(joint_name, world = True)
	        fol_joint_position = cmds.xform(follicleTransform, query = True, worldSpace = True, translation = True)
	        cmds.xform(joint_name, worldSpace = True, translation = fol_joint_position)
	        cmds.parentConstraint(follicleTransform, joint_name, maintainOffset = True, weight = 1)
	        cmds.parent(joint_name, fol_jnt_group)
	    cmds.parent(fol_grp, lower_ribbon_grp)
	    cmds.parent(fol_jnt_group, lower_ribbon_grp)
	    skin_joint(fol_jnt_group)

	    lower_ctrl_grp = cmds.group(em = True, n = "lowerLip_all_ctrl_grp")
	    lower_sec_ctrl_grp = cmds.group(name = "lowerLip_sec_ctrl_grp", empty = True)

	    lower_jnt_grp = cmds.group(em = True, n = "lowerLip_jnt_grp")
	    lower_sec_jnt_grp = cmds.group(name = "lowerLip_sec_jnt_grp", empty = True)
	    cmds.parent(lower_sec_jnt_grp, lower_jnt_grp)


	    cmds.parent(lower_ctrl_grp, "Lip_All_grp")
	    cmds.parent(lower_sec_ctrl_grp, lower_ctrl_grp)
	    cmds.parent("lowerLip_jnt_grp", "noTransform_grp")
	    cmds.parent("lower_ribbon_grp", "noTransform_grp")

	    all_follicles = cmds.listRelatives(fol_grp, c = True) or []

	    created_circle = {}
	    created_joint = {}

	    mid_index = len(all_follicles)//2
	    for index, follicle in enumerate(all_follicles):
	    	if index == 2:
    			create_controller_and_joint(cmds.getAttr(follicle + ".translate")[0], "B_tri", "R_lowerLip", lower_sec_ctrl_grp, lower_sec_jnt_grp)
    		if index == mid_index:
    			create_controller_and_joint(cmds.getAttr(follicle + ".translate")[0], "mid", "mid_lowerLip", lower_sec_ctrl_grp, lower_sec_jnt_grp)
    			create_controller_and_joint(cmds.getAttr(follicle + ".translate")[0], "down", "lowerLip", lower_sec_ctrl_grp, lower_sec_jnt_grp)
    		if index == len(all_follicles) - 2:
	        	create_controller_and_joint(cmds.getAttr(follicle + ".translate")[0], "A_tri", "L_lowerLip", lower_sec_ctrl_grp, lower_sec_jnt_grp)
	    num_elements_each_side = (len(all_follicles)-1)//2
	    print(num_elements_each_side)
	    mid_upper = ((len(all_follicles) - 3) + mid_index) // 2
	    mid_lower = (3 + mid_index)//2

	    mid_between_mid_and_mid_lower = (mid_index + mid_lower) // 2
	    mid_between_mid_and_mid_upper = (mid_index + mid_upper) // 2
	    mid_between_mid_lower_and_end = (mid_lower + 1) // 2 
	    mid_between_mid_upper_and_end = (mid_upper + (len(all_follicles) - 1)) // 2 

	    for i in range(2, num_elements_each_side -2):
	        index_right = mid_index + i
	        index_left = mid_index - i
	        if index_left == mid_lower:
        		create_controller_and_joint(cmds.getAttr(all_follicles[index_left] + ".translate")[0], "B2_sec", "R_lowerLip", lower_sec_ctrl_grp, lower_sec_jnt_grp)
        		create_controller_and_joint(cmds.getAttr(all_follicles[mid_between_mid_and_mid_lower] + ".translate")[0], "B1_sec", "R_lowerLip", lower_sec_ctrl_grp, lower_sec_jnt_grp)
        		create_controller_and_joint(cmds.getAttr(all_follicles[mid_between_mid_lower_and_end] + ".translate")[0], "B_sec", "R_lowerLip", lower_sec_ctrl_grp, lower_sec_jnt_grp)

        	if index_right == mid_upper:
        		create_controller_and_joint(cmds.getAttr(all_follicles[index_right] + ".translate")[0], "A2_sec", "L_lowerLip", lower_sec_ctrl_grp, lower_jnt_grp)
        		create_controller_and_joint(cmds.getAttr(all_follicles[mid_between_mid_and_mid_upper] + ".translate")[0], "A1_sec", "L_lowerLip", lower_sec_ctrl_grp, lower_sec_jnt_grp)
        		create_controller_and_joint(cmds.getAttr(all_follicles[mid_between_mid_upper_and_end] + ".translate")[0], "A_sec", "L_lowerLip", lower_sec_ctrl_grp, lower_sec_jnt_grp)

	if loft[0] == "loft_upper_created":
		upper_joint_selected = cmds.listRelatives("upperLip_sec_jnt_grp", ad = True, type = "joint")
		upper_loft_skin = cmds.skinCluster(upper_joint_selected, "loft_upper_created", name  = "upper_loft_skinCluster", tsb = True)
	if loft[0] == "loft_lower_created":
		lower_joint_selected = cmds.listRelatives("lowerLip_sec_jnt_grp", ad = True, type = "joint")
		lower_loft_skin = cmds.skinCluster(lower_joint_selected, "loft_lower_created", name  = "lower_loft_skinCluster", tsb = True)
		upper_corner_jnt_selected = cmds.listRelatives("upperLip_sec_jnt_grp", ad = True, type = "joint")
		for jnt in upper_corner_jnt_selected:
			if jnt == "L_upper_A_jnt" or jnt == "R_upper_B_jnt":
				cmds.setAttr(jnt +".liw", 0)
				cmds.skinCluster(lower_loft_skin, e = True, ai = jnt, ug = True, dr = 4, ps = 0, ns = 10)

def create_cheek_controller_and_joint(*args):
	cheek_gen_jnt_grp = cmds.group(name = "cheek_jnt_grp", empty = True)
	cheek_gen_ctrl_grp = cmds.group(name = "cheek_ctrl_grp", empty = True)
	cheek_skin_jnt_grp = "skin_jnt_grp"
	cheek_jnt_data = cmds.listRelatives(cheek_skin_jnt_grp, allDescendents = True, type = "joint")

	for index, cheek_jnt in enumerate(cheek_jnt_data):
		pos = cmds.xform(cheek_jnt, query = True, worldSpace = True, translation = True)
		cheek_loc_grp = cmds.group(name  = f"L_cheek_{index}_loc_jnt_grp", empty = True)
		cheek_dup_jnt = cmds.duplicate(cheek_jnt, name = f"L_cheek_{index}_setDrv_jnt")

		cheek_jnt_offset_grp = cmds.group(name  = f"L_cheek_{index}_jnt_offset_grp" )

		cheek_ctrl = cmds.circle(name = f"L_cheek_{index}_ctrl", radius = 0.3)[0]
		cheek_grp = cmds.group(name = f"L_cheek_{index}_offset_grp", empty = True)
		cmds.parent(cheek_ctrl,cheek_grp)
		cmds.parent(cheek_grp, cheek_gen_ctrl_grp)

		cmds.xform(cheek_loc_grp, ws = True, translation = pos)
		cmds.xform(cheek_grp, ws = True, translation = pos)
		cmds.setAttr(cheek_ctrl + ".translateZ", 1)

		cmds.parent(cheek_jnt_offset_grp, cheek_dup_jnt)
		cmds.parent(cheek_loc_grp, cheek_gen_jnt_grp)
		cmds.parent(cheek_dup_jnt, cheek_loc_grp)

		cmds.parent(cheek_dup_jnt, "setDrv_jnt_grp")
		cmds.parentConstraint("head_jnt", "jaw_jnt", cheek_dup_jnt, mo = True, w = 1)

		if index == "1":
			expression_str = """
						L_cheek_1_loc_jnt_grp.translateX = L_cheek_1_setDrv_jnt.translateX + L_upper_corner_A_ctrl.translateX/2 + name_upLip_Move_ctrl.translateX/2 + name_Lip_Move_ctrl.translateX/2;
						L_cheek_1_loc_jnt_grp.translateY = L_cheek_1_setDrv_jnt.translateY + L_upper_corner_A_ctrl.translateY/2.5 + name_upLip_Move_ctrl.translateY/2 + name_Lip_Move_ctrl.translateY/2;
						L_cheek_1_loc_jnt_grp.rotateX = L_cheek_1_setDrv_jnt.rotateX;
						L_cheek_1_loc_jnt_grp.rotateY = L_cheek_1_setDrv_jnt.rotateY;
						L_cheek_1_loc_jnt_grp.rotateZ = L_cheek_1_setDrv_jnt.rotateZ;
						L_cheek_1_loc_jnt_grp.translateZ = L_cheek_1_setDrv_jnt.translateZ + L_upper_corner_A_ctrl.translateZ/2 + name_upLip_Move_ctrl.translateZ/2 + name_Lip_Move_ctrl.translateZ/2;
					"""
		if index == "2":
			expression_str = """
						$percent = L_upper_corner_A_ctrl_.cheekUp;
						L_cheek_2_loc_jnt_grp.translateX = L_cheek_2_setDrv_jnt.translateX + L_upper_corner_A_ctrl_.translateX * $percent/1.5;
						L_cheek_2_loc_jnt_grp.translateY = L_cheek_2_setDrv_jnt.translateY + L_upper_corner_A_ctrl_.translateY * $percent/1.5;
						L_cheek_2_loc_jnt_grp.rotateX = L_cheek_2_setDrv_jnt.rotateX;
						L_cheek_2_loc_jnt_grp.rotateY = L_cheek_2_setDrv_jnt.rotateY;
						L_cheek_2_loc_jnt_grp.rotateZ = L_cheek_2_setDrv_jnt.rotateZ;
						if (L_upper_corner_A_ctrl_.translateY >= 0)
						L_cheek_2_loc_jnt_grp.translateZ = L_cheek_2_setDrv_jnt.translateZ + L_upper_corner_A_ctrl_.translateZ * $percent/4 + L_upper_corner_A_ctrl_.translateY * $percent/3;
						else
						L_cheek_2_loc_jnt_grp.translateZ = L_cheek_2_setDrv_jnt.translateZ + L_upper_corner_A_ctrl_.translateZ * $percent/4 + L_upper_corner_A_ctrl_.translateY * $percent/18;
					"""
			if cmds.objExists('L_upper_corner_A_ctrl'):
				cmds.expression(s = expression_str, name = 'l_cheek_exp')
			else:
				print("Nesne mevcut değil!")

		if index == 3:

			expression_str = """
							$percent=R_upper_corner_B_ctrl.cheekUp;
						mid_cheek_loc_grp.translateX = mid_cheek_setDrv_jnt.translateX + R_upper_corner_B_ctrl.translateX * $percent/1.5;
						mid_cheek_loc_grp.translateY = mid_cheek_setDrv_jnt.translateY + R_upper_corner_B_ctrl.translateY * $percent/1.5;
						mid_cheek_loc_grp.rotateX = mid_cheek_setDrv_jnt.rotateX;
						mid_cheek_loc_grp.rotateY = mid_cheek_setDrv_jnt.rotateY;
						mid_cheek_loc_grp.rotateZ = mid_cheek_setDrv_jnt.rotateZ;
						if (R_upper_corner_B_ctrl.translateY >= 0)
						mid_cheek_loc_grp.translateZ = mid_cheek_setDrv_jnt.translateZ + R_upper_corner_B_ctrl.translateZ * $percent/4 + R_upper_corner_B_ctrl.translateY * $percent/3;
						else
						mid_cheek_loc_grp.translateZ = mid_cheek_setDrv_jnt.translateZ + R_upper_corner_B_ctrl.translateZ * $percent/4 + R_upper_corner_B_ctrl.translateY * $percent/18;
						"""
			if cmds.objExists('R_upper_corner_B_ctrl'):
				cmds.expression(s = expression_str, name='l_cheekUp_exp')
			else:
				print("Nesne mevcut değil!")

	cmds.parent(cheek_gen_ctrl_grp, "head_ctrl")
	cmds.parent(cheek_gen_jnt_grp, "noTransform_grp")	


def create_curve_position(num_edges, curve):
	cheek_ctrl_grp = cmds.group(name = "cheek_ctrl_grp", empty = True)
	cheek_jnt_grp = cmds.group(name = "cheek_jnt_grp", empty = True)

	min_param = cmds.getAttr(curve + ".minValue")
	max_param = cmds.getAttr(curve + ".maxValue")

	mid_param = (min_param + max_param) // 2
	mid_R_param = (min_param + mid_param) // 2
	mid_L_param = (mid_param + max_param) // 2

	print(f"Eğrinin parametre aralığı: {min_param} - {max_param}")
	
	mid_point = num_edges // 2
	mid_L_side = (num_edges + mid_point) // 2
	mid_R_side = mid_point // 2

	mid_L_up_side = (num_edges + mid_L_side ) // 2
	mid_L_down_side = (mid_L_side + mid_point) // 2

	mid_R_up_side = mid_R_side  // 2
	mid_R_down_side = (mid_R_side + mid_point) // 2

	start_pos = cmds.pointOnCurve(curve, pr = min_param, position = True)
	end_pos = cmds.pointOnCurve(curve, pr = max_param, position = True)
	mid_pos = cmds.pointOnCurve(curve, pr = mid_param, position = True)
	mid_L_pos = cmds.pointOnCurve(curve, pr = mid_L_side, position = True)
	mid_L_up_pos = cmds.pointOnCurve(curve, pr = mid_L_up_side, position = True)
	mid_L_down_pos = cmds.pointOnCurve(curve, pr = mid_L_down_side, position = True)
	mid_R_pos = cmds.pointOnCurve(curve, pr = mid_R_side, position = True)
	mid_R_up_pos = cmds.pointOnCurve(curve, pr = mid_R_up_side, position = True)
	mid_R_down_pos = cmds.pointOnCurve(curve, pr = mid_R_down_side, position = True)

	for num in range(num_edges + 1):
		if num == 0:
			create_cheek_controller_and_joint(start_pos, cheek_ctrl_grp, cheek_jnt_grp, "L_02","cheek")
		if num == num_edges:
			create_cheek_controller_and_joint(end_pos, cheek_ctrl_grp, cheek_jnt_grp, "L_01","cheek")
		if num == mid_point:
			create_cheek_controller_and_joint(mid_pos, cheek_ctrl_grp, cheek_jnt_grp, "mid","cheek")
			
	cmds.parent(cheek_ctrl_grp, "head_ctrl")
	cmds.parent(cheek_jnt_grp, "noTransform_grp")	

def process_textField(text_field, curve_group_name, loft_name):
    selected_edges = cmds.textField(text_field, query = True, text = True)
    
    selected_edges_list = selected_edges.split(',')
    cmds.select(selected_edges_list)

    if not selected_edges:
        cmds.warning(f"No edges selected in {text_field}.")
        return None, None

    num_edges = len(selected_edges.split(','))
    selected_edges = cmds.ls(selection = True)

    curve = cmds.polyToCurve(form = 2, degree = 3)[0]
    cmds.xform(curve, centerPivots = True)
    cmds.delete(curve, ch = True)

    curve_grp = cmds.group(em = True, name = curve_group_name)
    cmds.parent(curve, curve_grp)

    dup_curve = cmds.duplicate(curve, smartTransform = True)[0]
    cmds.xform(dup_curve, centerPivots = True)
    cmds.delete(dup_curve, ch=True)

    cmds.setAttr(dup_curve + ".translateZ", -0.2)
    loft = cmds.loft(curve, dup_curve, n = loft_name, ch = True, polygon = 0)[0]
    createFol(num_edges, [loft])
    cmds.parent(loft, "crv_loft_grp")

    cmds.parent(curve_grp, "crv_loft_grp")
    cmds.hide(curve_grp)

    return selected_edges, num_edges

def build(*args):
    first_selected, first_num_edges = process_textField(first_tool, "curve_upper_grp", "loft_upper_created")
    second_selected, second_num_edges = process_textField(second_tool, "curve_lower_grp", "loft_lower_created")
    create_cheek_controller_and_joint()

    if not first_selected and not second_selected:
        cmds.warning("No edges selected in either text field.")

def select_model(*args):
    select = cmds.ls(selection = True, flatten = True)
    model_str = ",".join(select)
    cmds.textField(model_tool, edit = True, text = model_str)

def select_main_upper_edges(*args):
    selected_edges_main_upper = cmds.ls(selection = True, flatten = True)
    edges_str = ",".join(selected_edges_main_upper)
    cmds.textField(first_tool, edit = True, text = edges_str)

def select_main_lower_edges(*args):
    selected_edges_main_lower = cmds.ls(selection = True, flatten = True)
    edges_str = ",".join(selected_edges_main_lower)
    cmds.textField(second_tool, edit = True, text = edges_str)

def window_setup():
	global model_tool, first_tool, second_tool, cheek_tool, cheek_vtx

	if cmds.window("RibbonTool", exists = True):
		cmds.deleteUI("RibbonTool", window = True)

	window = cmds.window("RibbonTool", title = "RibbonTool", widthHeight = (500,500))
	cmds.columnLayout(adjustableColumn = True)

	cmds.rowColumnLayout(numberOfColumns = 4, columnWidth = [(1, 120), (2, 100), (3, 100), (4, 100)], columnSpacing = [(1, 10), (2, 10), (3, 10), (4, 10)], rowSpacing = [1, 6])
	cmds.button(label = "Select Model", command = select_model)
	model_tool = cmds.textField()
	cmds.button(label = "Create Joints", command = build_joints)
	cmds.button(label = "Create Ctrl and Skin", command = create_control_and_skin)
	cmds.setParent("..")

	cmds.rowColumnLayout(numberOfColumns = 3, columnWidth = [(1, 150), (2, 100), (3, 120)], columnSpacing = [(1, 10), (2, 10), (3, 10)], rowSpacing = [1, 5])
	cmds.button(label = "Select Upper Lip Edges", command = select_main_upper_edges)
	first_tool = cmds.textField()
	cmds.setParent("..")

	cmds.rowColumnLayout(numberOfColumns = 3, columnWidth = [(1, 150), (2, 100), (3, 120)], columnSpacing = [(1, 10), (2, 10), (3, 10)], rowSpacing = [1, 5])
	cmds.button(label = "Select Lower Lip Edges", command = select_main_lower_edges)
	second_tool = cmds.textField()
	cmds.setParent("..")

	cmds.rowColumnLayout(numberOfColumns = 5, columnWidth = [(1, 150), (2, 100), (3, 120)], columnSpacing = [(1, 10), (2, 10), (3, 10)], rowSpacing = [1, 5])
	cmds.button(label = "Cheek Points", command = create_cheek_bones)
	cmds.setParent("..")

	cmds.rowColumnLayout(numberOfColumns = 3, columnWidth = [(1, 120), (2, 200), (3, 50)], columnSpacing=[(1, 10), (2, 10), (3, 10)], rowSpacing=[10, 10])
	cmds.text(label = "")
	cmds.button(label = "Build", command = build, width = 50)  # Smaller width for the button
	cmds.text(label = "")
	cmds.setParent("..")
	cmds.showWindow("RibbonTool")

window_setup()
