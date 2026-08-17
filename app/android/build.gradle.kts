allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

val newBuildDir: File = if (System.getenv("CI") != null) {
    file("${rootProject.projectDir}/build")
} else {
    file("C:/build_lang")
}
rootProject.layout.buildDirectory.set(newBuildDir)

subprojects {
    project.layout.buildDirectory.set(file("${newBuildDir}/${project.name}"))
}
subprojects {
    project.evaluationDependsOn(":app")
}

