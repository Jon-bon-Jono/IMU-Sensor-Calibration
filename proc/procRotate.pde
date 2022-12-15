import peasy.org.apache.commons.math.geometry.Rotation;
import peasy.org.apache.commons.math.geometry.RotationOrder;
import peasy.org.apache.commons.math.geometry.CardanEulerSingularityException;
import processing.opengl.*;
import processing.serial.*;

Serial sp;
String buffer = null;
float[] q;
double[] r; //rotation angles, rotation order XYZ
int eos = 35; //ascii for '#', the delimiter of transmitted madgwick data
private Rotation q_rotation;
PShape model; 

//Initial orientation of the pshape
float init_z_rot = PI/2;
float init_x_rot = 9*PI/8;
float init_y_rot = PI/2;
float model_scale = 20;

void setup() {
  size(900, 900, P3D);
  
  //Load PShape
  model = loadShape("hand/16834_hand_v1_NEW.obj").getTessellation();
  println("Shape loaded");
  model.scale(model_scale);
  model.rotateX(init_x_rot);
  model.rotateY(init_y_rot);
  model.rotateZ(init_z_rot);
  
  sp = new Serial(this, "COM5", 19200);
  sp.clear();
  buffer = null;
  // Throw out the first reading
  while (sp.available() > 0) {
    buffer = sp.readStringUntil(eos);
  }
  buffer=null;
  q = new float[4]; // [w,x,y,z]
  r = new double[3];
}

void draw() {
  background(0); 
  lights();
  stroke(255);
  strokeWeight(16);
  // render a point in the center
  point(width/2 + 100, height/2, 0);
  strokeWeight(5);
  camera(0,0,-600, width/2 + 100, height/2, 0, 0.0, 0.0, 1.0);
  translate(width/2, height/2);
   
  //Listen for Madgwick quaternion
  while (sp.available() > 0) {
    buffer = sp.readStringUntil(eos);
    if (buffer != null) {
      String[] imu_data = split(buffer, ' ');
      if(imu_data[3]==null || imu_data[4]==null || imu_data[5]==null || imu_data[6]==null){return;}
      q[0] = float(imu_data[3]);
      q[1] = float(imu_data[4]);
      q[2] = float(imu_data[5]);
      q[3] = float(imu_data[6].replaceAll(",",""));
      println("w:"+q[0]+", x:"+q[1]+", y:"+q[2]+", z:"+q[3]);
      break;
    }
  }
  
  q_rotation = new Rotation(q[0], q[1], q[2], q[3], false);
  try {
    r = q_rotation.getAngles(RotationOrder.XYZ);
  } catch (final CardanEulerSingularityException e) {
  }
  //println("x:"+(r[0]*180)/PI+", y:"+(r[1]*180)/PI+", z:"+(r[2]*180)/PI);
  
  //Roll,Pitch,Yaw angles method -- still getting singularity from Pitch
  pushMatrix();
  rotateX(-(float) r[0]);
  rotateY((float) r[1]);
  rotateZ((float) r[2]);
  shape(model);
  popMatrix();
  
  /*
  //Rotation matrix method -- still getting singularity from Pitch
  pushMatrix();
  float c1 = cos((float) r[0]);
  float s1 = sin((float) r[0]);
  float c2 = cos((float) -r[2]);
  float s2 = sin((float) -r[2]);
  float c3 = cos((float) -r[1]);
  float s3 = sin((float) -r[1]);
  applyMatrix( c2*c3, s1*s3+c1*c3*s2, c3*s1*s2-c1*s3, 0,-s2, c1*c2, c2*s1, 0,c2*s3, c1*s2*s3-c3*s1, c1*c3+s1*s2*s3, 0,0, 0, 0, 1);
  shape(model);
  popMatrix();
  */
  
  drawAxes(5000);
  
}
 
void drawAxes(float size){
  //X  - red
  stroke(100,0,0);
  line(-size,0,0,0,0,0);
  stroke(192,0,0);
  line(0,0,0,size,0,0);
  //Y - green
  stroke(0,100,0);
  line(0,-size,0,0,0,0);
  stroke(0,192,0);
  line(0,0,0,0,size,0);
  //Z - blue
  stroke(0,0,192);
  line(0,0,-size,0,0,0);
  stroke(0,0,100);
  line(0,0,0,0,0,size);
}
